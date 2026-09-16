"""
Dynatrace AI Observability Workshop
====================================
Sample RAG (Retrieval Augmented Generation) Service

This is a simple AI-powered Q&A service that uses:
- OpenAI for LLM capabilities
- ChromaDB for vector storage
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
import chromadb
from chromadb.config import Settings
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Get configuration from environment
ATTENDEE_ID = os.getenv("ATTENDEE_ID", "workshop-attendee")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

# Lifespan event handler (replaces deprecated @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
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
    initialize_rag()
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
    use_rag: bool = True
    simulate_errors: bool = False

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    attendee_id: str
    sources: Optional[List[str]] = None

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
# Knowledge Base - Sample Documents about Dynatrace
# ═══════════════════════════════════════════════════════════════════════════

SAMPLE_DOCUMENTS = [
    """
    Dynatrace is an AI-powered, full-stack observability platform that provides 
    automatic and intelligent monitoring for cloud-native and enterprise environments. 
    It uses Davis AI to automatically detect anomalies, identify root causes, and 
    provide precise answers about application performance issues.
    """,
    """
    Dynatrace OneAgent is a single agent that automatically discovers and monitors 
    all processes, services, and infrastructure in your environment. It requires 
    no manual configuration and provides full-stack visibility from the application 
    layer down to the infrastructure.
    """,
    """
    OpenTelemetry is an open-source observability framework that provides APIs, 
    libraries, and tools for collecting telemetry data. Dynatrace fully supports 
    OpenTelemetry and can ingest traces, metrics, and logs via the OTLP protocol.
    """,
    """
    Grail is Dynatrace's next-generation data lakehouse that provides unified 
    storage and analysis of all observability data. It enables powerful analytics, 
    custom dashboards, and AI-powered insights across logs, traces, metrics, 
    and business events.
    """,
    """
    Dynatrace Application Security provides runtime vulnerability detection and 
    protection. It automatically identifies vulnerabilities in your running 
    applications without requiring code changes or additional agents.
    """,
    """
    OpenLLMetry is an open-source project built on OpenTelemetry for monitoring 
    LLM applications. It provides automatic instrumentation for popular AI/ML 
    frameworks like OpenAI, LangChain, and more, enabling observability into 
    AI workloads.
    """,
    """
    The Dynatrace MCP (Model Context Protocol) server enables AI assistants to 
    interact with Dynatrace environments. It allows querying Dynatrace data, 
    analyzing problems, and getting insights directly from your IDE using 
    tools like GitHub Copilot.
    """
]

# ═══════════════════════════════════════════════════════════════════════════
# RAG Components Initialization
# ═══════════════════════════════════════════════════════════════════════════

# Initialize embeddings and vector store
embeddings = None
vectorstore = None
qa_chain = None
retriever = None
llm = None

def format_docs(docs):
    """Format retrieved documents into a single string"""
    return "\n\n".join(doc.page_content for doc in docs)

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
        "message": "Embedding model 'text-embedding-3-large' returned null vector for input chunk",
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
        "message": "Azure OpenAI returned malformed JSON in function call response",
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
        "message": "Semantic search returned 0 documents with similarity score > 0.7 threshold",
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
        "message": "Content filter triggered: Response blocked due to policy violation (category: hate_speech, severity: medium)",
        "log_level": "warning",
        "error_code": "CONTENT_FILTER_BLOCK"
    },
    {
        "exception": EmbeddingServiceError,
        "message": "Token count mismatch: Expected 512 tokens, received 0 from embedding endpoint",
        "log_level": "error",
        "error_code": "EMB_TOKEN_MISMATCH"
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

@task(name="retrieve_documents")
def retrieve_documents(query: str) -> list:
    """
    Step 1: Retrieve relevant documents from vector store
    This generates embedding + vector search spans
    """
    if not retriever:
        logger.warning("Document retrieval skipped - retriever not initialized")
        return []
    docs = retriever.invoke(query)
    logger.info("Documents retrieved from vector store", extra={
        "query_length": len(query),
        "documents_found": len(docs)
    })
    return docs

@task(name="generate_context")
def generate_context(docs: list) -> str:
    """
    Step 2: Format retrieved documents into context string
    """
    if not docs:
        return "No relevant context found."
    return format_docs(docs)

# Extended system prompt for Azure OpenAI prompt caching (requires 1,024+ tokens)
RAG_SYSTEM_PROMPT = """You are an expert AI assistant for the Dynatrace AI Observability Workshop, 
specializing in application performance monitoring, distributed tracing, and AI/LLM observability.
You provide accurate, helpful, and technically detailed responses about observability, monitoring,
and software instrumentation topics.

## Your Expertise Areas

### 1. Dynatrace Platform Overview
Dynatrace is the leading AI-powered observability platform that provides automatic and intelligent 
monitoring for cloud-native and enterprise environments. Key capabilities include:

- **Full-stack observability**: End-to-end visibility from user experience to infrastructure
- **Automatic discovery and instrumentation**: OneAgent technology that requires no manual configuration
- **Davis AI engine**: Automatic root cause analysis, anomaly detection, and problem remediation
- **Grail data lakehouse**: Unified storage and analysis of all observability data at scale
- **Distributed tracing with PurePath**: Complete transaction visibility across microservices
- **Real User Monitoring (RUM)**: Track actual user sessions and experiences
- **Session Replay**: Visual playback of user sessions for debugging
- **Synthetic monitoring**: Proactive testing from global locations
- **Log management and analytics**: Unified log ingestion, search, and correlation
- **Infrastructure monitoring**: Hosts, containers, Kubernetes, cloud platforms
- **Application security**: Runtime vulnerability detection and protection (RASP)
- **Business analytics**: Custom metrics, dashboards, and business event tracking

### 2. OpenTelemetry Integration
Dynatrace fully supports the OpenTelemetry standard for collecting telemetry data:

- **OTLP ingestion**: Send traces, metrics, and logs via the /api/v2/otlp endpoint
- **Trace context propagation**: W3C Trace Context and Baggage support
- **Semantic conventions**: Standard attribute naming for consistent data
- **Custom instrumentation**: Add spans and attributes to your code
- **Span events and links**: Capture additional context within traces
- **Resource attributes**: Service name, version, environment metadata
- **Instrumentation libraries**: Auto-instrumentation for Python, Java, Node.js, .NET, Go
- **Collector support**: Route data through OpenTelemetry Collector

### 3. AI/LLM Observability with OpenLLMetry
OpenLLMetry (by Traceloop) extends OpenTelemetry for AI/ML workloads:

- **Automatic instrumentation**: Works with LangChain, OpenAI, Azure OpenAI, Anthropic, Cohere
- **Token tracking**: Monitor prompt tokens, completion tokens, and total usage
- **Latency measurement**: Track response times for LLM and embedding calls
- **Vector database tracing**: ChromaDB, Pinecone, Weaviate, Milvus query visibility
- **Cost estimation**: Calculate spending based on token consumption and model pricing
- **Workflow decorators**: @workflow and @task for creating trace hierarchies
- **Association properties**: Add business context like user ID, session ID, conversation ID
- **Prompt/response capture**: Optional logging of inputs and outputs for debugging
- **Model versioning**: Track which model versions are used in production
- **Error tracking**: Capture and analyze LLM failures and rate limits

### 4. LangChain Framework
LangChain is a popular framework for building LLM applications:

- **RAG pipelines**: Retrieval Augmented Generation for knowledge-enhanced responses
- **LCEL (LangChain Expression Language)**: Declarative chain composition
- **Document loaders**: Ingest data from files, URLs, databases, APIs
- **Text splitters**: Chunk documents for embedding and retrieval
- **Vector stores**: Integration with ChromaDB, Pinecone, Weaviate, FAISS
- **Retrievers**: Query vector stores with semantic search
- **Chat models**: Interface with OpenAI, Azure OpenAI, Anthropic, local models
- **Embeddings**: Generate vector representations of text
- **Prompt templates**: Reusable, parameterized prompts
- **Output parsers**: Structure LLM responses into typed objects
- **Memory**: Maintain conversation history across interactions
- **Agents**: LLM-powered decision making and tool use
- **Callbacks**: Hook into chain execution for logging and monitoring

### 5. Azure OpenAI Service
Microsoft's enterprise-grade LLM platform with unique capabilities:

- **Model availability**: GPT-4, GPT-4o, GPT-4o-mini, GPT-3.5-Turbo
- **Embedding models**: text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large
- **API versioning**: Use stable or preview versions for new features
- **Prompt caching**: Reduce costs and latency with cached prompt prefixes (1024+ tokens)
- **Content filtering**: Built-in responsible AI content moderation
- **Private endpoints**: VNet integration for secure connectivity
- **Managed identity**: Azure AD authentication without API keys
- **Regional deployment**: Choose regions for data residency and latency
- **Provisioned throughput**: Reserved capacity for predictable performance
- **Fine-tuning**: Customize models with your own training data

### 6. Workshop Lab Topics
This workshop covers hands-on exercises in AI observability:

- **Lab 0 - Environment Setup**: Configure GitHub Codespaces, install dependencies, set environment variables
- **Lab 1 - Instrumentation**: Add OpenLLMetry/Traceloop to a Python RAG application
- **Lab 2 - Trace Exploration**: Analyze AI traces in Dynatrace, understand spans and attributes
- **Lab 3 - Dynatrace MCP**: Use Model Context Protocol for agentic AI workflows with Copilot

## Response Guidelines

When answering questions, follow these principles:

1. **Accuracy**: Provide technically accurate information based on the context provided
2. **Clarity**: Explain concepts clearly for intermediate developers who may be new to observability
3. **Code Examples**: Include complete, working code snippets when helpful (use Python by default)
4. **Best Practices**: Recommend observability and instrumentation best practices
5. **Actionable**: Provide specific next steps when answering how-to questions
6. **Formatting**: Use markdown for code blocks, lists, headers, and emphasis
7. **Conciseness**: Be thorough but avoid unnecessary verbosity
8. **Context-aware**: Reference the provided context when relevant to the question

## Context from Knowledge Base
{context}

Based on the context above and your expertise, provide a helpful response to the user's question.
If the context doesn't contain relevant information, draw upon your knowledge of the topics listed above.
"""

@task(name="generate_response")
def generate_response(question: str, context: str) -> str:
    """
    Step 3: Generate LLM response with context
    This generates the main LLM completion span
    """
    if not llm:
        raise ValueError("LLM not initialized")
    
    # Use chat messages format for cleaner trace capture
    from langchain_core.messages import SystemMessage, HumanMessage
    
    # Use extended system prompt (1,024+ tokens enables Azure OpenAI prompt caching)
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    
    response = llm.invoke(messages)
    return response.content

def summarize_sources(docs: list) -> list:
    """
    Step 4: Extract and summarize source snippets
    """
    if not docs:
        return []
    return [doc.page_content[:100] + "..." for doc in docs]

@task(name="analyze_query_intent")
def analyze_query_intent(query: str) -> dict:
    """
    Step 5: Quick LLM call to classify query intent
    This adds an additional LLM span for richer traces
    """
    if not llm:
        return {"intent": "unknown", "confidence": 0}
    
    # Use messages format for consistent trace capture
    from langchain_core.messages import HumanMessage
    
    classification_prompt = f"""Classify the following query into one of these categories: 
    'technical', 'conceptual', 'troubleshooting', 'general'. 
    Respond with just the category name.
    
    Query: {query}"""
    
    result = llm.invoke([HumanMessage(content=classification_prompt)])
    return {"intent": result.content.strip().lower(), "query": query}

def initialize_rag():
    """Initialize the RAG components with sample documents"""
    global embeddings, vectorstore, qa_chain, retriever, llm
    
    try:
        # Initialize Azure OpenAI embeddings
        embeddings = AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            azure_deployment=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            api_version=AZURE_OPENAI_API_VERSION
        )
        
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        # Split documents
        docs = text_splitter.create_documents(SAMPLE_DOCUMENTS)
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=f"workshop_{ATTENDEE_ID}"
        )
        
        # Create retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Initialize Azure OpenAI LLM (stored globally for reuse)
        llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
            api_version=AZURE_OPENAI_API_VERSION,
            temperature=0.7,
            model=AZURE_OPENAI_CHAT_DEPLOYMENT
        )
        
        # Create prompt template (uses extended system prompt for caching)
        prompt = ChatPromptTemplate.from_template(RAG_SYSTEM_PROMPT + "\n\nQuestion: {question}\n\nAnswer:")
        
        # Create RAG chain using LCEL
        qa_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        logger.info("RAG system initialized successfully", extra={
            "attendee_id": ATTENDEE_ID,
            "embedding_model": AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            "chat_model": AZURE_OPENAI_CHAT_DEPLOYMENT,
            "document_count": len(SAMPLE_DOCUMENTS)
        })
        print(f"✅ RAG initialized successfully for attendee: {ATTENDEE_ID}")
        return True
        
    except Exception as e:
        logger.error("Failed to initialize RAG system", extra={
            "attendee_id": ATTENDEE_ID,
            "error": str(e)
        })
        print(f"❌ Failed to initialize RAG: {e}")
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
        status="healthy",
        attendee_id=ATTENDEE_ID,
        service_name=f"ai-chat-service-{ATTENDEE_ID}"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        attendee_id=ATTENDEE_ID,
        service_name=f"ai-chat-service-{ATTENDEE_ID}"
    )

@workflow(name="rag_chat_pipeline")
def process_rag_chat(message: str) -> tuple:
    """
    RAG Chat Pipeline - Groups all LLM calls under a single parent trace
    """
    # Step 1: Analyze query intent (generates LLM span)
    intent_info = analyze_query_intent(message)
    
    # Step 2: Retrieve relevant documents (generates embedding + search spans)
    retrieved_docs = retrieve_documents(message)
    
    # Step 3: Generate context from documents
    context = generate_context(retrieved_docs)
    
    # Step 4: Generate response with context (generates LLM span)
    response_text = generate_response(message, context)
    
    # Step 5: Summarize sources for response
    sources = summarize_sources(retrieved_docs)
    
    return response_text, sources


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - Process a message using RAG or direct LLM
    
    This endpoint generates multiple trace spans:
    1. Query intent analysis (LLM call)
    2. Document retrieval (embedding + vector search)
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
    
    # Add user's original question as a trace attribute for better visibility in Dynatrace
    # This captures the actual user input separately from the full RAG prompt
    # IMPORTANT: Set trace context FIRST so error logs correlate with the service
    try:
        from traceloop.sdk import Traceloop
        Traceloop.set_association_properties({
            "user.question": request.message,
            "use_rag": str(request.use_rag),
            "simulate_errors": str(request.simulate_errors)
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
            response_text, sources = process_rag_chat(request.message)
            logger.info("RAG chat response generated", extra={
                "response_length": len(response_text),
                "sources_count": len(sources) if sources else 0,
                "mode": "rag"
            })
        else:
            # Direct LLM call (single LLM span)
            direct_llm = AzureChatOpenAI(
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_API_KEY,
                azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT,
                api_version=AZURE_OPENAI_API_VERSION,
                temperature=0.7,
                model=AZURE_OPENAI_CHAT_DEPLOYMENT
            )
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
            sources=sources
        )
        
    except Exception as e:
        logger.error("Error processing chat request", extra={
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
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        docs = text_splitter.create_documents([request.content])
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
        "rag_initialized": qa_chain is not None,
        "documents_loaded": len(SAMPLE_DOCUMENTS),
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
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=True
    )
