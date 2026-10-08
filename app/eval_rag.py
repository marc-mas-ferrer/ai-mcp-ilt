"""
Retrieval check for the workshop knowledge base.

Run from the project root:

    python app/eval_rag.py          # offline: no LLM call, checks the context
    python app/eval_rag.py --llm    # also asks the chat model, RAG on and off

The offline check assembles the same context the app would send to the model
and asserts that the facts a good answer needs are in it, and that unrelated
topics are not. A topic match alone is not enough: the right section can be
retrieved while the fact inside it is cut off.

--llm needs the LLM_* values from .env. It asks every question three times and
fails a run if the RAG answer invents a name, lacks the attendee's service name or
an "In this workshop" section, or contains fewer than two of the key facts. The
RAG-off answer is printed for comparison.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from langchain_chroma import Chroma  # noqa: E402

import main  # noqa: E402

# question -> (facts the context must contain, topics that must not appear)
CASES = [
    ("What is Dynatrace?",
     ["Dynatrace Intelligence", "Smartscape", "OneAgent"],
     {"dql", "mcp"}),
    ("How does OpenTelemetry work?",
     ["OTLP", "exporter", "Collector"],
     {"dql", "mcp"}),
    ("How do I send OpenTelemetry data to Dynatrace?",
     ["/api/v2/otlp", "Api-Token", "openTelemetryTrace.ingest", "OTLPSpanExporter"],
     {"dql", "mcp"}),
    ("What is OpenLLMetry?",
     ["Traceloop", "gen_ai.usage.input_tokens", "@workflow"],
     {"dql", "mcp"}),
    ("How do I add OpenLLMetry to this app?",
     ["Traceloop.init", "api_endpoint", "Api-Token"],
     {"dql", "mcp"}),
    ("Explain Grail and DQL",
     ["data lakehouse", "fetch logs", "summarize"],
     {"openllmetry", "mcp"}),
    ("How do I calculate token cost?",
     ["gen_ai.usage.input_tokens", "per million"],
     {"dql", "mcp"}),
    ("What does the Dynatrace MCP server do?",
     ["Model Context Protocol", "GitHub Copilot"],
     {"dql", "openllmetry"}),
    ("How does this chatbot work?",
     ["rag_chat_pipeline", "retrieve_documents", "LocalHashingEmbeddings"],
     {"dql", "mcp"}),
    ("How do I find my traces in Dynatrace?",
     ["service.name", "ai-chat-service-"],
     {"mcp"}),
    ("What does EMB_NULL_VECTOR mean?",
     ["EMB_NULL_VECTOR", "null vector"],
     {"dql", "mcp"}),
]

# Each question is asked this many times in --llm mode, to check consistency.
REPEATS = 3

# Names a model invents when it has no real example to copy.
HALLUCINATION_MARKERS = [
    "DynatraceSpanExporter",
    "opentelemetry.exporter.dynatrace",
    "api/v1",
    "Bearer ",
    "SimpleConfig",
]


def build_store():
    docs, file_count = main.load_knowledge_base()
    main.KB_SECTIONS.clear()
    for doc in docs:
        main.KB_SECTIONS.setdefault(doc.metadata["topic"], []).append(doc)
    store = Chroma.from_documents(
        documents=docs,
        embedding=main.LocalHashingEmbeddings(dimensions=384),
        collection_name="eval_rag",
    )
    print(f"Knowledge files: {file_count}, sections: {len(docs)}\n")
    return store


def check_retrieval(store) -> tuple[int, dict]:
    failures = 0
    contexts = {}
    for question, facts, banned in CASES:
        docs = main.select_documents(store, question)
        context = main.generate_context(docs)
        contexts[question] = context

        missing = [f for f in facts if f not in context]
        if main.build_environment_block() not in context:
            missing.append("environment block")
        off_topic = sorted({d.metadata["topic"] for d in docs} & banned)
        ok = not missing and not off_topic
        failures += 0 if ok else 1

        print(f"{'PASS' if ok else 'FAIL'}  {question}  (~{len(context) // 4} tokens)")
        for source in main.summarize_sources(docs):
            print(f"        {source}")
        if missing:
            print(f"        MISSING FACTS: {missing}")
        if off_topic:
            print(f"        OFF-TOPIC: {off_topic}")
    return failures, contexts


def check_llm(contexts: dict) -> int:
    """Ask the real model with and without RAG and flag problems."""
    from langchain_core.messages import HumanMessage, SystemMessage

    missing_config = [
        n for n, v in {
            "LLM_BASE_URL": main.LLM_BASE_URL,
            "LLM_API_KEY": main.LLM_API_KEY,
        }.items() if not v
    ]
    if missing_config:
        print(f"\n--llm skipped, missing: {', '.join(missing_config)}")
        return 0

    rag_llm = main.make_chat_model(main.LLM_CHAT_MODEL, 0.2)
    plain_llm = main.make_chat_model(main.LLM_CHAT_MODEL, 0.7)

    failures = 0
    runs = [(q, f, b, run) for q, f, b in CASES for run in range(1, REPEATS + 1)]
    for question, facts, _, run in runs:
        rag_answer = rag_llm.invoke([
            SystemMessage(content=main.RAG_SYSTEM_PROMPT),
            HumanMessage(content=main.RAG_USER_TEMPLATE.format(
                context=contexts[question], question=question)),
        ]).content
        plain_answer = plain_llm.invoke(question).content

        invented = [m for m in HALLUCINATION_MARKERS if m in rag_answer]
        absent = [f for f in facts if f.lower() not in rag_answer.lower()]
        service = f"ai-chat-service-{main.ATTENDEE_ID}"
        lacks_service = service not in rag_answer
        lacks_workshop = "in this workshop" not in rag_answer.lower()
        too_few_facts = len(facts) - len(absent) < min(2, len(facts))
        failures += 1 if (invented or lacks_service or lacks_workshop or too_few_facts) else 0

        print(f"\n{'=' * 78}\n{question}  (run {run}/{REPEATS})")
        print(f"  RAG answer mentions facts: {len(facts) - len(absent)}/{len(facts)}"
              f"   not mentioned: {absent}")
        if invented:
            print(f"  INVENTED NAMES IN RAG ANSWER: {invented}")
        if lacks_service:
            print(f"  MISSING SERVICE NAME ({service}) IN RAG ANSWER")
        if lacks_workshop:
            print("  MISSING 'In this workshop' SECTION IN RAG ANSWER")
        if too_few_facts:
            print("  FEWER THAN 2 KEY FACTS IN RAG ANSWER")
        print(f"\n--- RAG ON ---\n{rag_answer}\n\n--- RAG OFF ---\n{plain_answer}")
    return failures


def main_eval() -> int:
    store = build_store()
    failures, contexts = check_retrieval(store)
    print(f"\n{len(CASES) - failures}/{len(CASES)} retrieval checks passed")

    if "--llm" in sys.argv:
        failures += check_llm(contexts)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main_eval())
