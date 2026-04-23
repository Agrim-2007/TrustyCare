"""
TrustyBot Agent State Definition

Defines the TypedDict state that flows through the LangGraph state machine.
Each node reads from and writes to this shared state object.
"""

from typing import TypedDict, Optional, List, Dict, Any

class TrustyCareState(TypedDict):
    """
    State object for the TrustyBot LangGraph agent.

    Flows through: classify → retrieve → generate → quality_gate → END
    """

    # ── Input ──────────────────────────────────────────────────────────
    user_message: str
    conversation_history: List[Dict[str, str]]  # [{role: "user"|"bot", content: str}]
    conversation_id: str

    # ── Classification output ──────────────────────────────────────────
    category: Optional[str]               # One of 7 categories
    detected_objection_id: Optional[str]   # Objection ID 1-10 or null
    primary_emotion: Optional[str]         # shame | fear | anxiety | pressure | etc.
    classification_confidence: Optional[str]  # high | medium | low

    # ── RAG output ────────────────────────────────────────────────────
    retrieved_context: Optional[str]       # Concatenated retrieved chunks
    retrieval_sources: Optional[List[str]] # Source URLs for citations

    # ── Generation output ─────────────────────────────────────────────
    proposed_response: Optional[str]       # Generated response (pre-quality gate)
    final_response: Optional[str]          # Final response (post-quality gate)

    # ── Quality gate output ───────────────────────────────────────────
    quality_verdict: Optional[str]         # pass | warn | fail
    quality_violations: Optional[List[str]]
    quality_score: Optional[Dict[str, Any]]

    # ── Metadata ──────────────────────────────────────────────────────
    handoff_triggered: bool
    regeneration_count: int                # Track regen attempts (max 1)
    error: Optional[str]
