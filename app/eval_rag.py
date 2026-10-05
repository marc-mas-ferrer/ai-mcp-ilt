"""
Offline retrieval check for the workshop knowledge base. No LLM is called.

Run from the project root:   python app/eval_rag.py
Prints the retrieved sections for each question and exits non-zero if the
expected topic is not among the top results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from langchain_chroma import Chroma  # noqa: E402

import main  # noqa: E402

# (question, topic that must appear in the top TOP_N retrieved chunks)
QUESTIONS = [
    ("What is Dynatrace?", "dynatrace"),
    ("What is OpenTelemetry?", "opentelemetry"),
    ("What is OpenLLMetry?", "openllmetry"),
    ("How do I send OpenTelemetry data to Dynatrace?", "opentelemetry"),
    ("How do I add Traceloop to this app?", "openllmetry"),
    ("What are the @workflow and @task decorators?", "openllmetry"),
    ("What is Grail?", "dql"),
    ("How do I write a DQL query to count errors by host?", "dql"),
    ("How do I calculate token cost?", "ai-observability"),
    ("What does the Dynatrace MCP server do?", "mcp"),
    ("What does EMB_NULL_VECTOR mean?", "workshop"),
]
TOP_N = 2


def main_eval() -> int:
    docs, file_count = main.load_knowledge_base()
    store = Chroma.from_documents(
        documents=docs,
        embedding=main.LocalHashingEmbeddings(dimensions=384),
        collection_name="eval_rag",
    )
    retriever = store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 12, "lambda_mult": 0.6},
    )
    print(f"Knowledge files: {file_count}, chunks: {len(docs)}\n")

    failures = 0
    for question, expected in QUESTIONS:
        results = retriever.invoke(question)
        topics = [d.metadata["topic"] for d in results[:TOP_N]]
        ok = expected in topics
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {question}  (expect: {expected})")
        for d in results:
            print(f"        {d.metadata['title']} - {d.metadata['section']}")

    print(f"\n{len(QUESTIONS) - failures}/{len(QUESTIONS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main_eval())
