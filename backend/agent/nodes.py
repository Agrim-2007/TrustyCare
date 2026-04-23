"""
TrustyBot LangGraph Node Functions

Each function represents a node in the LangGraph state machine.
Nodes read from and write to the shared TrustyCareState.

Pipeline: classify → retrieve → generate → quality_gate → [regenerate] → END
"""

import json
import os
from typing import Any

from groq import Groq
from dotenv import load_dotenv

from agent.prompts import (
    CLASSIFICATION_PROMPT,
    RAG_QUERY_PROMPT,
    RESPONSE_GENERATION_PROMPT,
    SELF_CHECK_PROMPT,
    SLAY_SYSTEM_PROMPT,
    REGENERATION_PROMPT,
    GROQ_MAIN_CONFIG,
    GROQ_CLASSIFIER_CONFIG,
    GROQ_QUALITY_GATE_CONFIG,
)
from rag.retriever import retriever

load_dotenv()

# ── Groq Client ──────────────────────────────────────────────────────────

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _call_groq(
    messages: list[dict],
    config: dict,
) -> str:
    """Make a Groq API call with the given config."""
    try:
        response = client.chat.completions.create(
            messages=messages,
            **config,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling Groq: {str(e)}"


def _format_history(history: list[dict], last_n: int = 3) -> str:
    """Format conversation history for prompt injection."""
    if not history:
        return "No previous conversation."

    recent = history[-last_n * 2 :]  # last N turns (user + bot pairs)
    lines = []
    for msg in recent:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 1: CLASSIFY MESSAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def classify_message(state: dict) -> dict:
    """
    Classify the user message into one of 7 categories.
    Returns classification metadata to the state.
    """
    prompt = CLASSIFICATION_PROMPT.format(
        user_message=state["user_message"],
        recent_history=_format_history(state.get("conversation_history", []), last_n=3),
    )

    result = _call_groq(
        messages=[{"role": "user", "content": prompt}],
        config=GROQ_CLASSIFIER_CONFIG,
    )

    # Parse JSON response
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        # Fallback classification
        parsed = {
            "category": "ambiguous",
            "detected_objection_id": None,
            "primary_emotion": None,
            "confidence": "low",
        }

    return {
        "category": parsed.get("category", "ambiguous"),
        "detected_objection_id": parsed.get("detected_objection_id"),
        "primary_emotion": parsed.get("primary_emotion"),
        "classification_confidence": parsed.get("confidence", "low"),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 2: RETRIEVE CONTEXT (RAG)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def retrieve_context(state: dict) -> dict:
    """
    Retrieve relevant context from the FAISS knowledge base.
    Uses RAG query optimization to get emotionally-relevant chunks.
    """
    # Generate optimized retrieval query
    rag_prompt = RAG_QUERY_PROMPT.format(
        user_message=state["user_message"],
        detected_objection=state.get("detected_objection_id", "none"),
        primary_emotion=state.get("primary_emotion", "none"),
    )

    optimized_query = _call_groq(
        messages=[{"role": "user", "content": rag_prompt}],
        config={
            "model": GROQ_MAIN_CONFIG["model"],
            "temperature": 0.0,
            "max_tokens": 50,
        },
    )

    # Retrieve from FAISS
    try:
        results = retriever.retrieve(
            query=optimized_query,
            top_k=4,
            emotion_filter=state.get("primary_emotion"),
        )
        context = retriever.format_context(results)
        sources = retriever.get_sources(results)
    except FileNotFoundError:
        context = "Knowledge base not yet indexed. Using system prompt only."
        sources = []

    return {
        "retrieved_context": context,
        "retrieval_sources": sources,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 3: GENERATE RESPONSE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_response(state: dict) -> dict:
    """
    Generate the chatbot response using classification + RAG context.
    The system prompt + generation prompt work together.
    """
    category = state.get("category", "ambiguous")

    # For adversarial/emotional/ambiguous — no RAG needed, use direct templates
    retrieved_context = state.get("retrieved_context", "No context retrieved.")

    generation_prompt = RESPONSE_GENERATION_PROMPT.format(
        category=category,
        detected_objection_id=state.get("detected_objection_id", "none"),
        primary_emotion=state.get("primary_emotion", "none"),
        retrieved_context=retrieved_context,
        conversation_history=_format_history(
            state.get("conversation_history", []), last_n=5
        ),
        user_message=state["user_message"],
    )

    # Use master system prompt as the system message
    system_prompt = SLAY_SYSTEM_PROMPT.format(
        retrieved_context=retrieved_context,
        conversation_history=_format_history(
            state.get("conversation_history", []), last_n=5
        ),
        user_message=state["user_message"],
    )

    response = _call_groq(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": generation_prompt},
        ],
        config=GROQ_MAIN_CONFIG,
    )

    # Check for handoff trigger
    handoff = any(
        phrase in response.lower()
        for phrase in ["trustycare advisor", "set that up", "book now", "connect you"]
    )

    return {
        "proposed_response": response,
        "final_response": response,  # Will be updated by quality gate
        "handoff_triggered": handoff,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 4: QUALITY GATE (SELF-CHECK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def self_check_response(state: dict) -> dict:
    """
    Quality gate — checks the proposed response for violations before sending.
    Returns verdict: pass, warn, or fail.
    """
    prompt = SELF_CHECK_PROMPT.format(
        user_message=state["user_message"],
        proposed_response=state.get("proposed_response", ""),
        category=state.get("category", "ambiguous"),
    )

    result = _call_groq(
        messages=[{"role": "user", "content": prompt}],
        config=GROQ_QUALITY_GATE_CONFIG,
    )

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        parsed = {"verdict": "pass", "violations": [], "regenerate": False}

    verdict = parsed.get("verdict", "pass")
    violations = parsed.get("violations", [])

    return {
        "quality_verdict": verdict,
        "quality_violations": violations,
        "final_response": state.get("proposed_response", ""),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 5: REGENERATE RESPONSE (on quality fail)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def regenerate_response(state: dict) -> dict:
    """
    Regenerate response when quality gate fails.
    Uses the failure context to produce a better response.
    Max 1 regeneration to prevent infinite loops.
    """
    regen_prompt = REGENERATION_PROMPT.format(
        score="< 82",
        violations=", ".join(state.get("quality_violations", [])),
        worst_aspect="Quality gate violations detected",
        user_message=state["user_message"],
        previous_response=state.get("proposed_response", ""),
        improvement_suggestion="Fix the listed violations while maintaining tone and length rules",
    )

    system_prompt = SLAY_SYSTEM_PROMPT.format(
        retrieved_context=state.get("retrieved_context", ""),
        conversation_history=_format_history(
            state.get("conversation_history", []), last_n=5
        ),
        user_message=state["user_message"],
    )

    response = _call_groq(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": regen_prompt},
        ],
        config=GROQ_MAIN_CONFIG,
    )

    handoff = any(
        phrase in response.lower()
        for phrase in ["trustycare advisor", "set that up", "book now", "connect you"]
    )

    return {
        "final_response": response,
        "handoff_triggered": handoff,
        "regeneration_count": state.get("regeneration_count", 0) + 1,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 6: HANDOFF (ready to proceed)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def route_to_handoff(state: dict) -> dict:
    """
    Handle 'ready_to_proceed' — respond with the handoff trigger message.
    """
    handoff_message = (
        "That's a brave and beautiful step. "
        "It sounds like you're ready to take the next step. I can connect you with a TrustyCare "
        "advisor — a real person who has helped hundreds of couples through this. They'll "
        "walk you through what the assessment involves and answer any questions. "
        "Want me to set that up?"
    )

    return {
        "final_response": handoff_message,
        "proposed_response": handoff_message,
        "handoff_triggered": True,
        "quality_verdict": "pass",
        "quality_violations": [],
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE 7: REFUSAL (medical questions)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def route_to_refusal(state: dict) -> dict:
    """
    Handle medical questions with the refusal template.
    """
    refusal_message = (
        "That's a question for a medical professional, not me — and I mean that in a good way. "
        "What I can do is connect you with a TrustyCare advisor who works with doctors and can "
        "give you a proper answer. Want me to do that?"
    )

    return {
        "final_response": refusal_message,
        "proposed_response": refusal_message,
        "handoff_triggered": False,
        "quality_verdict": "pass",
        "quality_violations": [],
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTING FUNCTIONS (for conditional edges)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def route_after_classify(state: dict) -> str:
    """Route from classification to the appropriate next node."""
    category = state.get("category", "ambiguous")

    routing = {
        "objection_explicit": "objection",
        "objection_implicit": "objection",
        "medical_question": "medical",
        "ready_to_proceed": "proceed",
        "adversarial": "adversarial",
        "emotional_escalation": "emotional",
        "ambiguous": "ambiguous",
    }

    return routing.get(category, "ambiguous")


def route_after_quality(state: dict) -> str:
    """Route from quality gate based on verdict."""
    verdict = state.get("quality_verdict", "pass")

    if verdict == "fail" and state.get("regeneration_count", 0) < 1:
        return "fail"

    if verdict == "warn":
        return "warn"

    return "pass"
