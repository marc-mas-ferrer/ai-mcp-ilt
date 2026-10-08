"""
Dynatrace AI Observability Workshop
====================================
Sample RAG (Retrieval Augmented Generation) Service

This is a simple AI-powered Q&A service that uses:
- Amazon Bedrock models (Nova Micro, Lite and Pro) through an
  OpenAI-compatible LiteLLM gateway
- Deterministic local vectorization for document retrieval
- ChromaDB for vector storage and similarity search
- LangChain for orchestration

🎯 WORKSHOP OBJECTIVE:
    Attendees will add OpenLLMetry/Traceloop instrumentation to this
    service to send traces to Dynatrace.
"""

import os
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Suppress OpenTelemetry warnings about None attribute values (from tracing libraries)
warnings.filterwarnings("ignore", message="Invalid type NoneType for attribute")

# Load environment variables from .env file in project root
# (handles both running from app/ directory and from project root)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Fall back to default behavior

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  🔬 LAB 1: INSTRUMENTATION SECTION                                        ║
# ║                                                                           ║
# ║  TODO: Add Dynatrace OpenLLMetry instrumentation here                    ║
# ║  Follow the instructions in the workshop guide to add the                 ║
# ║  Traceloop initialization code below this comment block.                  ║
# ║                                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# ---> ADD YOUR INSTRUMENTATION CODE HERE <---




# ════════════════════════════════════════════════════════════════════════════

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  📋 OPENTELEMETRY LOGGING TO DYNATRACE                                    ║
# ║                                                                           ║
# ║  This section configures OpenTelemetry logging to send logs to Dynatrace ║
# ║  via OTLP. Logs are automatically correlated with traces.                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource

# Get Dynatrace configuration for logging
DT_ENDPOINT = os.getenv("DT_ENDPOINT")
DT_API_TOKEN = os.getenv("DT_API_TOKEN")
ATTENDEE_ID_FOR_LOGS = os.getenv("ATTENDEE_ID", "workshop-attendee")

# Configure OpenTelemetry logging to Dynatrace
logger_provider = None
if DT_ENDPOINT and DT_API_TOKEN:
    # Create a resource with service name
    resource = Resource.create({
        "service.name": f"ai-chat-service-{ATTENDEE_ID_FOR_LOGS}"
    })
    
    # Set up the logger provider
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    
    # Configure OTLP log exporter - endpoint should be DT_ENDPOINT + /v1/logs
    log_endpoint = f"{DT_ENDPOINT}/v1/logs"
    print(f"📋 Log exporter endpoint: {log_endpoint}")
    
    log_exporter = OTLPLogExporter(
        endpoint=log_endpoint,
        headers={"Authorization": f"Api-Token {DT_API_TOKEN}"}
    )
    
    # Use BatchLogRecordProcessor with shorter export interval for faster delivery
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(log_exporter, schedule_delay_millis=1000)
    )
    
    # Attach OpenTelemetry handler to Python's root logger
    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(otel_handler)
    logging.getLogger().setLevel(logging.INFO)
    
    print("✅ OpenTelemetry Logging initialized - sending logs to Dynatrace")
else:
    # Set up basic logging if Dynatrace is not configured
    logging.basicConfig(level=logging.INFO)
    print("ℹ️  Dynatrace logging not configured (DT_ENDPOINT/DT_API_TOKEN not set)")

# Create a logger for this module
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
import hashlib
import math
import re



# Get configuration from environment
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# LLM gateway configuration (LiteLLM -> Amazon Bedrock)
# Model names are LiteLLM aliases such as "amazon-nova-lite"; the gateway maps
# each alias to a Bedrock inference profile.
LLM_BASE_URL        = os.getenv("LLM_BASE_URL")
LLM_API_KEY         = os.getenv("LLM_API_KEY")
LLM_CHAT_MODEL      = os.getenv("LLM_CHAT_MODEL", "amazon-nova-lite")      # default answer model
LLM_INTENT_MODEL    = os.getenv("LLM_INTENT_MODEL", "amazon-nova-micro")   # query classifier


def _csv(value: str) -> list:
    return [item.strip() for item in value.split(",") if item.strip()]


# Models the chat UI may select. The default answer model is always included.
LLM_AVAILABLE_MODELS = _csv(os.getenv(
    "LLM_AVAILABLE_MODELS",
    "amazon-nova-micro,amazon-nova-lite,amazon-nova-pro",
))
if LLM_CHAT_MODEL not in LLM_AVAILABLE_MODELS:
    LLM_AVAILABLE_MODELS.insert(0, LLM_CHAT_MODEL)



# Lifespan event handler (replaces deprecated @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("AI Chat Service starting", extra={
        "attendee_id": ATTENDEE_ID,
        "service_name": f"ai-chat-service-{ATTENDEE_ID}"
    })
    print(f"""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║         🚀 AI Chat Service Starting...                               ║
    ║                                                                      ║
    ║         Attendee ID: {ATTENDEE_ID:<43}║
    ║         Service: ai-chat-service-{ATTENDEE_ID:<28}║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    if not initialize_rag():
        raise RuntimeError(
            "RAG initialisation failed. Review the startup error above."
        )

    yield
    # Shutdown
    logger.info("AI Chat Service shutting down", extra={"attendee_id": ATTENDEE_ID})

# Initialize FastAPI app with attendee-specific naming
app = FastAPI(
    title=f"AI Chat Service - {ATTENDEE_ID}",
    description="A RAG-powered AI assistant for the Dynatrace AI Observability Workshop",
    version="1.0.0",
    lifespan=lifespan
)

# ═══════════════════════════════════════════════════════════════════════════
# FastAPI OpenTelemetry Instrumentation
# ═══════════════════════════════════════════════════════════════════════════

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Instrument FastAPI to create spans for all HTTP endpoints
# This creates parent spans that encompass downstream LLM/AI calls
FastAPIInstrumentor.instrument_app(app)
logger.info("FastAPI instrumented with OpenTelemetry", extra={
    "attendee_id": ATTENDEE_ID
})
print("✅ FastAPI instrumented - HTTP endpoints will create trace spans")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for UI
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ═══════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    model: Optional[str] = None   # LiteLLM alias; defaults to LLM_CHAT_MODEL
    use_rag: bool = True
    simulate_errors: bool = False

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    attendee_id: str
    sources: Optional[List[str]] = None
    model: Optional[str] = None

class DocumentRequest(BaseModel):
    """Request model for adding documents"""
    content: str
    metadata: Optional[dict] = None

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    attendee_id: str
    service_name: str

# ═══════════════════════════════════════════════════════════════════════════
# Knowledge Base - Markdown files in app/knowledge/
# ═══════════════════════════════════════════════════════════════════════════

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

# Each knowledge-base section is indexed as one chunk, prefixed with its title
# and section name, so a chunk about "Traceloop.init" still matches a query that
# only says "OpenLLMetry". Sections are only split when they exceed CHUNK_SIZE,
# so a block of related facts (such as the OTLP configuration) is never cut in
# half.
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150


def _parse_front_matter(raw: str) -> tuple[dict, str]:
    """Split a simple '---' delimited key: value header from the body."""
    if not raw.startswith("---"):
        return {}, raw
    _, header, body = raw.split("---", 2)
    meta = {}
    for line in header.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, body.strip()


def split_into_chunks(body: str, title: str, topic: str, source: str) -> list:
    """Split one markdown body by '##' section, then by size, tagging each chunk."""
    from langchain_core.documents import Document
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    sections = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("##", "section")]
    ).split_text(body)
    size_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = []
    for section_doc in sections:
        section = section_doc.metadata.get("section", "Overview")
        for text in size_splitter.split_text(section_doc.page_content):
            chunks.append(Document(
                page_content=f"{title} - {section}\n{text}",
                metadata={
                    "source": source,
                    "title": title,
                    "topic": topic,
                    "section": section,
                },
            ))
    return chunks


def load_knowledge_base(directory: Path = KNOWLEDGE_DIR) -> tuple[list, int]:
    """Load every markdown file in the knowledge directory as tagged chunks."""
    files = sorted(directory.glob("*.md"))
    chunks = []
    KB_KEYWORDS.clear()
    for path in files:
        meta, body = _parse_front_matter(path.read_text(encoding="utf-8"))
        keywords = [k.strip().lower() for k in meta.get("keywords", "").split(",")]
        if any(keywords):
            KB_KEYWORDS[meta.get("topic", path.stem)] = [k for k in keywords if k]
        chunks.extend(split_into_chunks(
            body,
            title=meta.get("title", path.stem),
            topic=meta.get("topic", path.stem),
            source=path.name,
        ))
    return chunks, len(files)


# Knowledge-base sections grouped by topic, in file order. Retrieval matches a
# single section, then returns the rest of that topic with it, so an answer to
# "How does X work?" sees the whole topic and not one fragment.
KB_SECTIONS: dict = {}

# Words that, when present in a question, select a topic directly (set by the
# 'keywords:' line in each knowledge file's front matter).
KB_KEYWORDS: dict = {}

# Sections from other topics are included only when they score nearly as well
# as the best match (distance within this factor of the best distance).
RELATED_SCORE_FACTOR = 1.15
MAX_RELATED_SECTIONS = 2
SEARCH_CANDIDATES = 8


# Number of knowledge files loaded, reported by /info.
KNOWLEDGE_FILE_COUNT = len(list(KNOWLEDGE_DIR.glob("*.md")))


# Question filler that appears in nearly every query and says nothing about the
# topic. Without this, "what is dynatrace" matches on "what" and "is" as strongly
# as on "dynatrace".
STOPWORDS = frozenset("""
a an and are as at be by can could do does for from how i if in into is it its
me my of on or please should tell that the their there this to us was we what
when where which who why will with would you your about explain describe give
""".split())


class LocalHashingEmbeddings(Embeddings):
    """
    Deterministic, dependency-free embeddings for the workshop RAG pipeline.

    The embedder converts lower-case word and character n-gram features into
    a fixed-size vector through stable SHA-256 feature hashing, then applies
    L2 normalisation. It makes no network calls and stores no external model.

    This is designed for a small, controlled workshop knowledge base. A
    production RAG implementation should normally use a trained embedding
    model for stronger semantic retrieval quality.
    """

    def __init__(self, dimensions: int = 384):
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than zero")
        self.dimensions = dimensions

    @staticmethod
    def _normalise_text(text: str) -> str:
        return " ".join(text.lower().split())

    @staticmethod
    def _word_features(text: str) -> list[str]:
        return re.findall(r"[a-z0-9][a-z0-9_.-]*", text)

    @staticmethod
    def _character_features(text: str) -> list[str]:
        compact = re.sub(r"\s+", " ", text)
        features: list[str] = []

        # Character n-grams improve resilience to related word forms,
        # punctuation and small spelling differences.
        for size in (3, 4, 5):
            if len(compact) < size:
                continue
            features.extend(
                f"char:{compact[index:index + size]}"
                for index in range(len(compact) - size + 1)
            )

        return features

    def _add_feature(
        self,
        vector: list[float],
        feature: str,
        weight: float,
    ) -> None:
        digest = hashlib.sha256(feature.encode("utf-8")).digest()
        index = int.from_bytes(digest[:8], "big") % self.dimensions
        sign = 1.0 if digest[8] % 2 == 0 else -1.0
        vector[index] += sign * weight

    def _embed(self, text: str) -> list[float]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        normalised = self._normalise_text(text)
        vector = [0.0] * self.dimensions

        if not normalised:
            return vector

        # Stopwords are dropped from word and bigram features only; the
        # character n-grams below still see the full text.
        words = [
            word for word in self._word_features(normalised)
            if word not in STOPWORDS
        ]

        # Whole words carry most of the retrieval signal.
        for word in words:
            self._add_feature(vector, f"word:{word}", weight=2.0)

        # Identifiers such as EMB_NULL_VECTOR or gen_ai.usage.input_tokens are
        # also indexed by their parts, so "null vector" or "input tokens" match.
        for word in words:
            parts = re.split(r"[_.-]", word)
            if len(parts) > 1:
                for part in parts:
                    if part and part not in STOPWORDS:
                        self._add_feature(vector, f"word:{part}", weight=1.0)

        # Adjacent word pairs preserve some local phrase information.
        for index in range(len(words) - 1):
            bigram = f"{words[index]} {words[index + 1]}"
            self._add_feature(vector, f"bigram:{bigram}", weight=1.5)

        # Character features add robustness for word variants and punctuation.
        for feature in self._character_features(normalised):
            self._add_feature(vector, feature, weight=0.25)

        magnitude = math.sqrt(sum(value * value for value in vector))

        if magnitude == 0.0:
            return vector

        return [value / magnitude for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)



# ═══════════════════════════════════════════════════════════════════════════
# RAG Components Initialization
# ═══════════════════════════════════════════════════════════════════════════

# Initialise embeddings and vector store
embeddings = None
vectorstore = None
retriever = None
llm = None          # default answer model
intent_llm = None   # cheap model that classifies the question


class ChatBedrockViaLiteLLM(ChatOpenAI):
    """
    Chat client for Amazon Bedrock models served through a LiteLLM gateway.

    LiteLLM speaks the OpenAI chat-completions protocol, so the transport is
    LangChain's ChatOpenAI. This subclass exists so the telemetry says what is
    really happening: OpenLLMetry names the span after the class
    (ChatBedrockViaLiteLLM.chat) and takes the provider from the class name and
    LangChain's ls_provider, so Dynatrace shows an AWS provider, not "openai".
    """

    def _get_ls_params(self, stop=None, **kwargs):
        params = super()._get_ls_params(stop=stop, **kwargs)
        params["ls_provider"] = "amazon_bedrock"
        return params


_model_clients: dict = {}


def make_chat_model(model: str, temperature: float = 0) -> ChatBedrockViaLiteLLM:
    """Return a cached chat client for one LiteLLM model alias."""
    key = (model, temperature)
    if key not in _model_clients:
        _model_clients[key] = ChatBedrockViaLiteLLM(
            model=model,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            temperature=temperature,
        )
    return _model_clients[key]


def format_docs(docs):
    """Format retrieved documents into a single string, labelled by source"""
    return "\n\n---\n\n".join(
        f"[Source: {doc.metadata.get('title', 'Knowledge base')}"
        f" - {doc.metadata.get('section', 'Overview')}]\n{doc.page_content.strip()}"
        for doc in docs
    )

# ═══════════════════════════════════════════════════════════════════════════
# Error Simulation for Workshop Demos
# ═══════════════════════════════════════════════════════════════════════════

import random
from opentelemetry import trace

# Get a tracer for creating spans around error simulation
tracer = trace.get_tracer(__name__)

class RAGPipelineError(Exception):
    """Custom exception for RAG pipeline errors"""
    pass

class EmbeddingServiceError(Exception):
    """Error when embedding service fails"""
    pass

class VectorStoreConnectionError(Exception):
    """Error when vector store connection fails"""
    pass

class LLMResponseError(Exception):
    """Error when LLM returns invalid response"""
    pass

class ContextWindowExceededError(Exception):
    """Error when context window is exceeded"""
    pass

class DocumentRetrievalError(Exception):
    """Error when document retrieval fails"""
    pass

SIMULATED_ERRORS = [
    {
        "exception": EmbeddingServiceError,
        "message": "Local vectorisation returned a null vector for the input chunk",
        "log_level": "error",
        "error_code": "EMB_NULL_VECTOR"
    },
    {
        "exception": VectorStoreConnectionError,
        "message": "ChromaDB collection 'workshop_documents' not found or corrupted",
        "log_level": "error",
        "error_code": "CHROMA_COLLECTION_ERR"
    },
    {
        "exception": LLMResponseError,
        "message": "The LLM gateway returned a malformed response",
        "log_level": "error",
        "error_code": "LLM_MALFORMED_RESPONSE"
    },
    {
        "exception": ContextWindowExceededError,
        "message": "Context window exceeded: 128,500 tokens provided, max is 128,000",
        "log_level": "error",
        "error_code": "CTX_WINDOW_EXCEEDED"
    },
    {
        "exception": DocumentRetrievalError,
        "message": "Vector search returned no relevant workshop documents",
        "log_level": "warning",
        "error_code": "DOC_NO_MATCHES"
    },
    {
        "exception": RAGPipelineError,
        "message": "RAG pipeline failed: LangChain chain execution timeout after 30 seconds",
        "log_level": "error",
        "error_code": "RAG_CHAIN_TIMEOUT"
    },
    {
        "exception": LLMResponseError,
        "message": "Guardrail intervened: Response blocked by Amazon Bedrock Guardrails (policy: content filter, category: hate, confidence: medium)",
        "log_level": "warning",
        "error_code": "CONTENT_FILTER_BLOCK"
    },
    {
        "exception": EmbeddingServiceError,
        "message": "Vector dimension mismatch: Expected 384 dimensions, received 0",
        "log_level": "error",
        "error_code": "EMB_DIMENSION_MISMATCH"
    }
]

def maybe_simulate_error(simulate: bool, stage: str = "processing"):
    """
    Simulate errors for workshop demonstration.
    This helps attendees learn to identify and debug errors in Dynatrace.
    Always triggers when enabled (100% rate for reliable demos).
    """
    if not simulate:
        return
    
    # Select a random error type
    error_config = random.choice(SIMULATED_ERRORS)
    
    # Debug print to confirm code is executing
    print(f"🐛 SIMULATING ERROR: {error_config['error_code']} - {error_config['message']}")
    
    # Log the error at ERROR level - always use error for simulated errors
    # so they show up clearly in Dynatrace with ERROR status
    log_message = f"[SIMULATED ERROR] {error_config['error_code']}: {error_config['message']}"
    
    # Always log at ERROR level for visibility in Dynatrace
    logger.error(log_message, extra={
        "error.code": error_config["error_code"],
        "error.message": error_config["message"],
        "error.stage": stage,
        "error.simulated": "true",
        "attendee.id": ATTENDEE_ID
    })
    
    # Force flush logs to Dynatrace before raising the exception
    if logger_provider:
        try:
            logger_provider.force_flush(timeout_millis=5000)
            print("✅ Logs flushed to Dynatrace")
        except Exception as flush_err:
            print(f"❌ Failed to flush logs: {flush_err}")
    else:
        print("⚠️ logger_provider is None - logs may not be sent to Dynatrace")
    
    raise error_config["exception"](error_config["message"])

# ═══════════════════════════════════════════════════════════════════════════
# RAG Pipeline Functions (Each creates distinct trace spans)
# ═══════════════════════════════════════════════════════════════════════════

# Import Traceloop decorators for creating trace hierarchies
try:
    from traceloop.sdk.decorators import workflow, task
    TRACELOOP_AVAILABLE = True
except ImportError:
    TRACELOOP_AVAILABLE = False
    # Define no-op decorators if Traceloop not available
    def workflow(name): return lambda f: f
    def task(name): return lambda f: f

def select_documents(store, query: str) -> list:
    """
    Pick the knowledge-base sections to show the model for a query.

    The main topic is decided in two steps. If the question names a topic by
    one of its front-matter keywords (for example "openllmetry" or "mcp"), that
    topic wins, because a stray word match in another section, such as "this
    app", must not outvote the term the user actually asked about. Otherwise the
    topic of the best-matching section is used. All sections of the main topic
    are returned in file order, followed by up to MAX_RELATED_SECTIONS sections
    from other topics that scored almost as well.
    """
    scored = store.similarity_search_with_score(query, k=SEARCH_CANDIDATES)
    if not scored:
        return []

    best_doc, best_score = scored[0]
    best_topic = best_doc.metadata.get("topic")

    # Topics named in the question; among them, prefer the best-scoring one.
    lowered = query.lower()
    named = {
        topic for topic, keywords in KB_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    }
    if named and best_topic not in named:
        for doc, _ in scored:
            if doc.metadata.get("topic") in named:
                best_topic = doc.metadata["topic"]
                break
        else:
            best_topic = sorted(named)[0]

    if best_topic in KB_SECTIONS:
        selected = list(KB_SECTIONS[best_topic])
    else:
        selected = [best_doc]

    related = 0
    for doc, score in scored[1:]:
        if related >= MAX_RELATED_SECTIONS:
            break
        if doc.metadata.get("topic") == best_topic:
            continue
        if score > best_score * RELATED_SCORE_FACTOR:
            break
        selected.append(doc)
        related += 1

    return selected


@task(name="retrieve_documents")
def retrieve_documents(query: str) -> list:
    """
    # Step 2: Generate a local query vector and search ChromaDB

    Local vectorisation occurs in-process and does not create a remote
    embedding-model span. ChromaDB uses the resulting vector to find the
    best-matching knowledge-base section, and the rest of that topic is
    returned with it.
    """
    if not vectorstore:
        logger.warning("Document retrieval skipped - vector store not initialized")
        return []
    docs = select_documents(vectorstore, query)
    logger.info("Documents retrieved from vector store", extra={
        "query_length": len(query),
        "documents_found": len(docs)
    })
    return docs

def build_environment_block() -> str:
    """
    Facts about this attendee's own running app. A general model cannot know any
    of this, so including it in every answer shows what RAG adds.
    """
    service = f"ai-chat-service-{ATTENDEE_ID}"
    return (
        "[Source: Your workshop environment]\n"
        "Facts about the attendee's own running app:\n"
        f"- Service name in Dynatrace: {service}\n"
        f"- Answer model (default): {LLM_CHAT_MODEL}\n"
        f"- Intent classification model: {LLM_INTENT_MODEL}\n"
        f"- Models you can select in the chat UI: {', '.join(LLM_AVAILABLE_MODELS)}\n"
        "- All models run on Amazon Bedrock, reached through the LiteLLM gateway; "
        "LLM spans are named ChatBedrockViaLiteLLM.chat\n"
        "- To find this app's traces in Dynatrace, run this DQL:\n"
        "fetch spans\n"
        f'| filter service.name == "{service}"\n'
        "| sort start_time desc\n"
        "| limit 20"
    )


@task(name="generate_context")
def generate_context(docs: list) -> str:
    """
    Step 2: Format retrieved documents into context string
    """
    if not docs:
        return (
            "No relevant reference material was found for this question.\n\n---\n\n"
            + build_environment_block()
        )
    return format_docs(docs) + "\n\n---\n\n" + build_environment_block()

# Static system prompt: behaviour and rules only. The facts come from the
# retrieved reference material, which is sent with the question (see
# RAG_USER_TEMPLATE). Keeping this prompt stable keeps requests comparable between
# models. Amazon Bedrock only caches a prompt prefix when the request marks a
# cache point, which this app does not do, so no prompt caching is expected.
RAG_SYSTEM_PROMPT = """You are an expert AI assistant for the Dynatrace AI Observability Workshop.
You help intermediate developers and SREs who are new to observability, and you
specialise in Dynatrace, OpenTelemetry, OpenLLMetry (Traceloop) and AI/LLM observability.
Each question arrives together with reference material taken from the workshop
knowledge base. The reference material is accurate and current for this workshop.

## How to use the reference material

1. Build your answer from the reference material first. Lead with the facts in it
   that a generic answer would not contain: product names, endpoints, token
   scopes, attribute names, commands and the way this workshop app is built.
2. Use the same names and terminology as the reference material. If it names a
   product feature one way and your own knowledge names it another way, use the
   reference material's name.
3. You may add short general background to make an answer easier to follow, but
   never let general knowledge contradict or replace the reference material.
4. Never invent Dynatrace-specific facts. If a detail such as an endpoint, a token
   scope, an environment variable or a package name is not in the reference
   material, do not guess it. Say that the knowledge base does not cover it.
5. If the reference material is labelled as not relevant or is empty, say so and
   answer briefly from general knowledge, clearly marked as general guidance.

## Rules for code

- Only show code that appears in the reference material, adapted to the question.
- Never invent package names, module paths, class names, function names, URLs
  or parameters. If you are not certain that something exists, leave it out.
- If the reference material has no code for the question, describe the steps in
  words and name the settings involved instead of writing code.
- Keep examples short and complete enough to run, and use Python by default.

## DQL syntax reference

Use this exact syntax when writing DQL. Do not invent alternatives.

A query starts with a data source and pipes records through commands:

fetch logs
| filter loglevel == "ERROR"
| summarize error_count = count(), by:{host.name}
| sort error_count desc
| limit 10

Aggregating spans with a calculated field:

fetch spans
| filter service.name == "checkout"
| filter isNotNull(gen_ai.usage.input_tokens)
| summarize total_input = sum(gen_ai.usage.input_tokens),
    request_count = count(),
    by:{gen_ai.response.model}
| fieldsAdd cost = total_input * 0.035 / 1000000.0
| sort total_input desc

Charting over time:

fetch spans
| filter service.name == "checkout"
| makeTimeseries request_count = count(), interval: 1m

Syntax rules:
- Commands are joined by the pipe character, one per line.
- Comparison uses ==, and string values use double quotes.
- filter takes a bare expression: filter loglevel == "ERROR"
- summarize takes named aggregates: summarize total = sum(field)
- Braces appear only in the by: clause, as by:{field.name}
- Field names containing dots are written as-is, unquoted.
- There is no semicolon at the end of a query.

Available commands: fetch, filter, fields, fieldsAdd, summarize, sort,
limit, lookup, makeTimeseries, parse, dedup, expand.

When the question concerns DQL, reproduce the syntax exactly as it appears in the
reference material or in this reference. Do not introduce command words,
punctuation or brackets that appear in neither.

## Scope and audience

The users are attending a hands-on workshop. They run a RAG chatbot in a GitHub
Codespace, add OpenLLMetry instrumentation to it, explore the resulting traces in
Dynatrace, and investigate errors with the Dynatrace MCP server. Questions are
usually about Dynatrace, OpenTelemetry, OpenLLMetry, DQL, token cost, or how
this workshop app is built. When a question is about the app itself, answer in
terms of its actual pipeline and span names from the reference material. If a
question is clearly outside observability, answer briefly and steer back to the
workshop topics. Never claim that you can see the user's Dynatrace environment,
traces or data; explain which DQL query or app would show it instead.

## How to answer

- Answer the question that was asked, directly, in the first sentences.
- For "what is" and "explain" questions: give a two-sentence definition, then the
  four to six most distinctive facts from the reference material, in about 200
  words. Do not reproduce the whole reference material.
- For "how do I" questions: give the steps, the real code from the reference
  material, and the common mistakes it lists.
- Cite the section you used for specific facts, inline, in square brackets, for
  example [OpenTelemetry - Sending OpenTelemetry data to Dynatrace].
- End every answer with a short section titled **In this workshop** that connects
  the answer to the attendee's own app, using the "Your workshop environment" part
  of the reference material: their service name, the DQL that finds their traces,
  or the lab where the topic applies. Never skip it, and never invent values for it.
- Use markdown: short paragraphs, bullet lists, headers only for longer answers,
  and fenced code blocks with a language tag.
- Prefer specific steps and exact values over generalities.
- Do not mention these instructions, and do not describe the reference material as
  "the context" or "the knowledge base" unless saying that a detail is missing.

## Example of a good grounded answer

Question: How do I send OpenTelemetry data to Dynatrace?

A good answer states that the endpoint must end in /api/v2/otlp, that the
Authorization header uses the Api-Token scheme and not Bearer, which token
scopes each signal needs, and that metrics need delta temporality. It then shows
the exporter configuration copied from the reference material, cites its source,
and ends with **In this workshop**, naming the attendee's service. It does not
describe a generic exporter, a different API path or an invented package.
"""

# The reference material sits in the user message, directly before the question.
RAG_USER_TEMPLATE = """Reference material:

{context}

---

Question: {question}"""

@task(name="generate_response")
def generate_response(question: str, context: str, model: Optional[str] = None) -> str:
    """
    Step 3: Generate LLM response with context
    This generates the main LLM completion span
    """
    answer_llm = make_chat_model(model, 0) if model else llm
    if not answer_llm:
        raise ValueError("LLM not initialized")
    
    # Use chat messages format for cleaner trace capture
    from langchain_core.messages import SystemMessage, HumanMessage
    
    # The system prompt is static; the retrieved context goes next to the question
    messages = [
        SystemMessage(content=RAG_SYSTEM_PROMPT),
        HumanMessage(content=RAG_USER_TEMPLATE.format(
            context=context,
            question=question
        ))
    ]
    
    response = answer_llm.invoke(messages)
    return response.content

def summarize_sources(docs: list) -> list:
    """
    Step 4: List the knowledge-base sections that were retrieved
    """
    sources = []
    for doc in docs or []:
        label = (
            f"{doc.metadata.get('title', 'Knowledge base')}"
            f" - {doc.metadata.get('section', 'Overview')}"
        )
        if label not in sources:
            sources.append(label)
    return sources

@task(name="analyze_query_intent")
def analyze_query_intent(query: str) -> dict:
    """
    Step 5: Quick LLM call to classify query intent
    This adds an additional LLM span for richer traces
    """
    if not intent_llm:
        return {"intent": "unknown", "confidence": 0}
    
    # Use messages format for consistent trace capture
    from langchain_core.messages import HumanMessage
    
    classification_prompt = f"""Classify the following query into one of these categories: 
    'technical', 'conceptual', 'troubleshooting', 'general'. 
    Respond with just the category name.
    
    Query: {query}"""
    
    result = intent_llm.invoke([HumanMessage(content=classification_prompt)])
    return {"intent": result.content.strip().lower(), "query": query}


def initialize_rag():
    """Initialise the local RAG components and LiteLLM chat client."""
    global embeddings, vectorstore, retriever, llm, intent_llm

    try:
        missing = [
            name
            for name, value in {
                "LLM_BASE_URL": LLM_BASE_URL,
                "LLM_API_KEY": LLM_API_KEY,
                "LLM_CHAT_MODEL": LLM_CHAT_MODEL,
                "LLM_INTENT_MODEL": LLM_INTENT_MODEL,
            }.items()
            if not value
        ]
        if missing:
            raise ValueError(
                "Missing required LLM configuration: " + ", ".join(missing)
            )

        # Initialise the deterministic local vectoriser.
        # This makes no network calls and downloads no external model.
        embeddings = LocalHashingEmbeddings(dimensions=384)

        # Load the markdown knowledge base as section-tagged chunks.
        docs, file_count = load_knowledge_base()
        if not docs:
            raise ValueError(f"No knowledge base content found in {KNOWLEDGE_DIR}")

        # Create an in-memory vector store using the same local vectoriser
        # for the workshop documents and subsequent attendee questions.
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=f"workshop_{ATTENDEE_ID}"
        )

        # Remember each topic's sections, in file order, so retrieval can return
        # the whole topic once one of its sections matches.
        KB_SECTIONS.clear()
        for doc in docs:
            KB_SECTIONS.setdefault(doc.metadata["topic"], []).append(doc)

        # Plain similarity retriever, used as the "retrieval is ready" signal
        # by the health check. Pipeline retrieval goes through select_documents.
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        # Chat clients for Amazon Bedrock models via the LiteLLM gateway.
        # The intent classifier and the answer model are separate models.
        llm = make_chat_model(LLM_CHAT_MODEL, 0)
        intent_llm = make_chat_model(LLM_INTENT_MODEL, 0)

        logger.info(
            "RAG system initialized successfully",
            extra={
                "attendee_id": ATTENDEE_ID,
                "embedding_model": "local-hashing-384",
                "chat_model": LLM_CHAT_MODEL,
                "intent_model": LLM_INTENT_MODEL,
                "document_count": file_count,
                "document_chunks": len(docs)
            }
        )

        print(
            f"✅ RAG initialized successfully for attendee: "
            f"{ATTENDEE_ID}"
        )
        print("   Vectoriser: local-hashing-384")
        print(f"   Knowledge files: {file_count}")
        print(f"   Documents indexed: {len(docs)}")
        print(f"   Answer model: {LLM_CHAT_MODEL}")
        print(f"   Intent model: {LLM_INTENT_MODEL}")
        print(f"   Selectable models: {', '.join(LLM_AVAILABLE_MODELS)}")

        return True

    except Exception as error:
        logger.exception(
            "Failed to initialize RAG system",
            extra={
                "attendee_id": ATTENDEE_ID,
                "error": str(error)
            }
        )

        print(f"❌ Failed to initialize RAG: {error}")
        return False

# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=FileResponse)
async def root():
    """Serve the chat UI"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/health", response_model=HealthResponse)
async def api_health():
    """API Health check with service information"""
    return HealthResponse(
        status="healthy" if retriever is not None and llm is not None else "degraded",
        attendee_id=ATTENDEE_ID,
        service_name=f"ai-chat-service-{ATTENDEE_ID}"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if retriever is not None and llm is not None else "degraded",
        attendee_id=ATTENDEE_ID,
        service_name=f"ai-chat-service-{ATTENDEE_ID}"
    )

@workflow(name="rag_chat_pipeline")
def process_rag_chat(message: str, model: Optional[str] = None) -> tuple:
    """
    RAG Chat Pipeline - Groups all LLM calls under a single parent trace
    """
    # Step 1: Analyze query intent (generates LLM span)
    analyze_query_intent(message)
    
    # Step 2: Generate a local query vector and search ChromaDB
    retrieved_docs = retrieve_documents(message)
    
    # Step 3: Generate context from documents
    context = generate_context(retrieved_docs)
    
    # Step 4: Generate response with context (generates LLM span)
    response_text = generate_response(message, context, model)
    
    # Step 5: Summarize sources for response
    sources = summarize_sources(retrieved_docs)
    
    return response_text, sources


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - Process a message using RAG or direct LLM
    
    This endpoint generates multiple trace spans:
    1. Query intent analysis (LLM call)
    2. Local vectorisation and ChromaDB document retrieval
    3. Context generation
    4. Response generation (LLM call)
    5. Source summarization
    """
    logger.info("Chat request received", extra={
        "message_length": len(request.message),
        "use_rag": request.use_rag,
        "simulate_errors": request.simulate_errors,
        "attendee_id": ATTENDEE_ID
    })
    
    if not request.message.strip():
        logger.warning("Empty message rejected")
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    model = request.model or LLM_CHAT_MODEL
    if model not in LLM_AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model '{model}'. Available: {', '.join(LLM_AVAILABLE_MODELS)}"
        )
    
    # Add user's original question as a trace attribute for better visibility in Dynatrace
    # This captures the actual user input separately from the full RAG prompt
    # IMPORTANT: Set trace context FIRST so error logs correlate with the service
    try:
        from traceloop.sdk import Traceloop
        Traceloop.set_association_properties({
            "user.question": request.message,
            "use_rag": str(request.use_rag),
            "simulate_errors": str(request.simulate_errors),
            "llm.selected_model": model
        })
    except Exception:
        pass  # Traceloop not initialized, skip
    
    # Simulate errors for workshop demonstration if enabled
    # This happens AFTER trace context is set so logs correlate with the service
    # Wrap in a span to ensure trace context is available for log correlation
    try:
        with tracer.start_as_current_span("error_simulation") as span:
            span.set_attribute("simulate_errors", request.simulate_errors)
            maybe_simulate_error(request.simulate_errors, stage="pre_processing")
    except (RAGPipelineError, EmbeddingServiceError, VectorStoreConnectionError, 
            LLMResponseError, ContextWindowExceededError, DocumentRetrievalError) as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    try:
        if request.use_rag and retriever and llm:
            # Use the workflow-decorated function to group all operations
            response_text, sources = process_rag_chat(request.message, model)
            logger.info("RAG chat response generated", extra={
                "response_length": len(response_text),
                "sources_count": len(sources) if sources else 0,
                "mode": "rag"
            })
        else:
            # Direct LLM call (single LLM span)
            direct_llm = make_chat_model(model, 0.7)

            response = direct_llm.invoke(request.message)
            response_text = response.content
            sources = None
            logger.info("Direct LLM response generated", extra={
                "response_length": len(response_text),
                "mode": "direct"
            })
        
        return ChatResponse(
            response=response_text,
            attendee_id=ATTENDEE_ID,
            sources=sources,
            model=model
        )
        
    except Exception as e:
        logger.exception("Error processing chat request", extra={
            "error": str(e),
            "attendee_id": ATTENDEE_ID
        })
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/documents")
async def add_document(request: DocumentRequest):
    """Add a document to the knowledge base"""
    if not vectorstore:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        metadata = request.metadata or {}
        docs = split_into_chunks(
            request.content,
            title=metadata.get("title", "User document"),
            topic=metadata.get("topic", "user"),
            source=metadata.get("source", "api"),
        )
        vectorstore.add_documents(docs)
        
        return {"status": "success", "message": "Document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

@app.get("/info")
async def get_info():
    """Get detailed service information"""
    return {
        "service_name": f"ai-chat-service-{ATTENDEE_ID}",
        "attendee_id": ATTENDEE_ID,
        "rag_initialized": retriever is not None and llm is not None,
        "vectoriser": "local-hashing-384",
        "chat_model": LLM_CHAT_MODEL,
        "intent_model": LLM_INTENT_MODEL,
        "available_models": LLM_AVAILABLE_MODELS,
        "documents_loaded": KNOWLEDGE_FILE_COUNT,
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Service info"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/chat", "method": "POST", "description": "Chat with AI"},
            {"path": "/documents", "method": "POST", "description": "Add documents"},
        ]
    }

# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print(f"Starting AI Chat Service for attendee: {ATTENDEE_ID}")
    uvicorn.run(
        app,  # pass the object, not "main:app", so the module is not imported twice
        host=APP_HOST,
        port=APP_PORT,
        # No auto-reload: it re-imports this module in extra processes, which
        # initialises OpenTelemetry again and logs duplicate warnings.
        # Stop (Ctrl+C) and restart the app after editing it.
        reload=False
    )
