"""
TrustyBot FastAPI Application

Main API server for the objection-handling chatbot.

Endpoints:
  POST /chat — Send a message, get a response through the LangGraph pipeline
  GET  /health — Health check
"""

import os
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# ── Validate environment ────────────────────────────────────────────────

if not os.getenv("GROQ_API_KEY"):
    print("⚠ WARNING: GROQ_API_KEY not set. Copy .env.example to .env and add your key.")

# ── FastAPI App ─────────────────────────────────────────────────────────

app = FastAPI(
    title="TrustyBot API",
    description="Objection-handling chatbot for TrustyCare pre-marriage health assessments",
    version="1.0.0",
)

# CORS for frontend (Vite dev server)
FRONTEND_URL = os.getenv("FRONTEND_URL", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        FRONTEND_URL
    ] if FRONTEND_URL else [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ───────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'bot'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message", min_length=1)
    conversation_id: Optional[str] = Field(
        default=None, description="Conversation ID for session continuity"
    )
    conversation_history: list[ChatMessage] = Field(
        default_factory=list, description="Previous messages in this conversation"
    )


class ChatResponse(BaseModel):
    response: str = Field(..., description="TrustyBot's response")
    category: str = Field(..., description="Classified category of the user's message")
    handoff_triggered: bool = Field(
        default=False, description="Whether a handoff to advisor was triggered"
    )
    sources: list[str] = Field(
        default_factory=list, description="RAG source URLs used"
    )
    conversation_id: str = Field(..., description="Conversation ID")
    quality_verdict: Optional[str] = Field(
        default=None, description="Quality gate verdict"
    )


# ── Endpoints ───────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "TrustyBot API",
        "model": "llama-3.3-70b-versatile",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    Runs the user's message through the LangGraph pipeline:
    classify → retrieve → generate → quality_gate → response
    """
    # Lazy import to avoid slow startup
    from agent.graph import trustycare_graph

    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Build initial state
    initial_state = {
        "user_message": request.message,
        "conversation_history": [
            {"role": m.role, "content": m.content}
            for m in request.conversation_history
        ],
        "conversation_id": conversation_id,
        # Classification outputs (filled by nodes)
        "category": None,
        "detected_objection_id": None,
        "primary_emotion": None,
        "classification_confidence": None,
        # RAG outputs
        "retrieved_context": None,
        "retrieval_sources": None,
        # Generation outputs
        "proposed_response": None,
        "final_response": None,
        # Quality gate
        "quality_verdict": None,
        "quality_violations": None,
        "quality_score": None,
        # Metadata
        "handoff_triggered": False,
        "regeneration_count": 0,
        "error": None,
    }

    try:
        # Run the LangGraph pipeline
        result = trustycare_graph.invoke(initial_state)

        return ChatResponse(
            response=result.get("final_response", "I'm sorry, I couldn't generate a response. Please try again."),
            category=result.get("category", "unknown"),
            handoff_triggered=result.get("handoff_triggered", False),
            sources=result.get("retrieval_sources") or [],
            conversation_id=conversation_id,
            quality_verdict=result.get("quality_verdict"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}",
        )


# ── Startup event ───────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Warm up the retriever on startup."""
    print("🚀 TrustyBot API starting...")
    try:
        from rag.retriever import retriever
        retriever._load()
        print("✅ FAISS index loaded successfully")
    except FileNotFoundError:
        print("⚠ FAISS index not found. Run 'python rag/ingest.py' to build it.")
    except Exception as e:
        print(f"⚠ Error loading FAISS index: {e}")
    print("🤖 TrustyBot API ready!")
