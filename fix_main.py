from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "app/main.py")
if not path.exists():
    raise SystemExit(f"ERROR: {path} not found")

text = path.read_text(encoding="utf-8")
original = text

# Undo HTML entities if they were accidentally pasted into the Python source.
entity_replacements = {
    "&lt;=": "<=",
    "-&gt;": "->",
    "&gt;": ">",
    "&lt;": "<",
}
for old, new in entity_replacements.items():
    text = text.replace(old, new)

# Remove literal HTML line breaks if they were accidentally pasted into source.
text = re.sub(r"(?m)^\s*<br(?:\s+aria-hidden=\"true\")?>\s*$", "", text)

# Clean the module description.
text = text.replace(
    "- OpenAI for LLM capabilities\n- ChromaDB for vector storage\n- LangChain for orchestration",
    "- Amazon Nova Micro through an OpenAI-compatible LiteLLM gateway\n"
    "- Deterministic local vectorisation for document retrieval\n"
    "- ChromaDB for vector storage and similarity search\n"
    "- LangChain for orchestration",
)

# Remove accidental whitespace in dotenv loading.
text = text.replace("if env_path.exists():\n    \n    load_dotenv(env_path)",
                    "if env_path.exists():\n    load_dotenv(env_path)")

# Ensure the workshop marker is valid Python text, not escaped HTML.
text = text.replace("# ---&gt; ADD YOUR INSTRUMENTATION CODE HERE &lt;---",
                    "# --> ADD YOUR INSTRUMENTATION CODE HERE <--")

# Correct stale wording.
text = text.replace("# LLM Gateway Configuration (LiteLLM -> Amazon Bedrock)",
                    "# LLM gateway configuration (LiteLLM -> Amazon Bedrock)")
text = text.replace("# Initialize OpenAI LLM (stored globally for reuse)",
                    "# Initialise the OpenAI-compatible LiteLLM chat client.")
text = text.replace("# Create prompt template (uses extended system prompt for caching)",
                    "# Create the RAG prompt containing the retrieved context.")
text = text.replace(
    "# Step 2: Retrieve relevant documents (generates embedding + search spans)",
    "# Step 2: Generate a local query vector and search ChromaDB",
)
text = text.replace(
    "Step 1: Retrieve relevant documents from vector store\n    This generates embedding + vector search spans",
    "Step 1: Generate a local query vector and retrieve relevant documents.\n\n"
    "    Local vectorisation occurs in-process and does not create a remote\n"
    "    embedding-model span. ChromaDB uses the resulting vector to find the\n"
    "    most relevant document chunks.",
)

# Correct simulated-error messages after removal of hosted embeddings.
text = text.replace(
    "Embedding model 'text-embedding-3-large' returned null vector for input chunk",
    "Local vectorisation returned a null vector for the input chunk",
)
text = text.replace(
    "Token count mismatch: Expected 512 tokens, received 0 from embedding endpoint",
    "Vector dimension mismatch: Expected 384 dimensions, received 0",
)
text = text.replace('"error_code": "EMB_TOKEN_MISMATCH"',
                    '"error_code": "EMB_DIMENSION_MISMATCH"')
text = text.replace(
    "Semantic search returned 0 documents with similarity score > 0.7 threshold",
    "Vector search returned no relevant workshop documents",
)

# Fail fast if RAG initialisation fails.
text = re.sub(
    r"(?m)^(\s*)initialize_rag\(\)\n\1yield$",
    r'\1if not initialize_rag():\n'
    r'\1    raise RuntimeError(\n'
    r'\1        "RAG initialisation failed. Review the startup error above."\n'
    r'\1    )\n\n'
    r'\1yield',
    text,
)

# Replace a stale lifespan docstring spelling if present.
text = text.replace(
    '"""Lifespan context manager for startup/shutdown events"""',
    '"""Manage application startup and shutdown."""',
)

# Require all gateway settings before building the client.
needle = '''def initialize_rag():
    """Initialize the RAG components with sample documents."""
    global embeddings, vectorstore, qa_chain, retriever, llm

    try:
'''
replacement = '''def initialize_rag():
    """Initialise the local RAG components and LiteLLM chat client."""
    global embeddings, vectorstore, qa_chain, retriever, llm

    try:
        missing = [
            name
            for name, value in {
                "LLM_BASE_URL": LLM_BASE_URL,
                "LLM_API_KEY": LLM_API_KEY,
                "LLM_CHAT_MODEL": LLM_CHAT_MODEL,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(
                "Missing required LLM configuration: " + ", ".join(missing)
            )

'''
if needle in text:
    text = text.replace(needle, replacement, 1)

# Make health endpoints report RAG readiness honestly.
text = text.replace(
    'status="healthy",\n        attendee_id=ATTENDEE_ID,',
    'status="healthy" if retriever is not None and llm is not None else "degraded",\n'
    '        attendee_id=ATTENDEE_ID,',
)

# Add vectoriser details to /info if absent.
text = text.replace(
    '"rag_initialized": qa_chain is not None,\n        "documents_loaded": len(SAMPLE_DOCUMENTS),',
    '"rag_initialized": retriever is not None and llm is not None,\n'
    '        "vectoriser": "local-hashing-384",\n'
    '        "chat_model": LLM_CHAT_MODEL,\n'
    '        "documents_loaded": len(SAMPLE_DOCUMENTS),',
)

# Use logger.exception when processing fails so stack traces are available.
text = text.replace(
    'logger.error("Error processing chat request", extra={',
    'logger.exception("Error processing chat request", extra={',
)

# Avoid unused intent result while keeping the classification span.
text = text.replace(
    "intent_info = analyze_query_intent(message)",
    "analyze_query_intent(message)",
)

# Normalise common British spelling in newly migrated labels only.
text = text.replace("Local vectorization", "Local vectorisation")
text = text.replace("Initialize the RAG", "Initialise the RAG")
text = text.replace("Initialize embeddings", "Initialise embeddings")

# Basic migration invariants.
required = [
    "class LocalHashingEmbeddings(Embeddings):",
    "embeddings = LocalHashingEmbeddings(dimensions=384)",
    '"embedding_model": "local-hashing-384"',
    "model=LLM_CHAT_MODEL",
    "api_key=LLM_API_KEY",
    "base_url=LLM_BASE_URL",
]
missing_required = [item for item in required if item not in text]
if missing_required:
    raise SystemExit(
        "ERROR: Refusing to write because required migrated constructs are missing:\n- "
        + "\n- ".join(missing_required)
    )

forbidden = [
    "HuggingFaceEmbeddings",
    "LOCAL_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
    "AzureChatOpenAI",
    "AzureOpenAIEmbeddings",
]
remaining = [item for item in forbidden if item in text]
if remaining:
    raise SystemExit(
        "ERROR: Refusing to write because legacy constructs remain:\n- "
        + "\n- ".join(remaining)
    )

backup = path.with_suffix(path.suffix + ".before-final-cleanup")
if not backup.exists():
    backup.write_text(original, encoding="utf-8")

path.write_text(text, encoding="utf-8")
print(f"Updated: {path}")
print(f"Backup:  {backup}")
