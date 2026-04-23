"""
TrustyBot LangGraph Agent Graph

Builds the state machine that powers the TrustyBot conversation pipeline.

Graph flow:
  classify → [route] → retrieve → generate → quality_gate → [regenerate] → END
                     → handoff → END
                     → refusal → END
                     → generate (adversarial/emotional/ambiguous) → quality_gate → END
"""

from langgraph.graph import StateGraph, END

from agent.state import TrustyCareState
from agent.nodes import (
    classify_message,
    retrieve_context,
    generate_response,
    self_check_response,
    regenerate_response,
    route_to_handoff,
    route_to_refusal,
    route_after_classify,
    route_after_quality,
)


def build_trustycare_graph():
    """
    Build and compile the TrustyBot LangGraph state machine.

    Returns a compiled graph that can be invoked with a TrustyCareState dict.
    """
    graph = StateGraph(TrustyCareState)

    # ── Define nodes ──────────────────────────────────────────────────
    graph.add_node("classify", classify_message)
    graph.add_node("retrieve", retrieve_context)
    graph.add_node("generate", generate_response)
    graph.add_node("quality_gate", self_check_response)
    graph.add_node("regenerate", regenerate_response)
    graph.add_node("handoff", route_to_handoff)
    graph.add_node("refusal", route_to_refusal)

    # ── Entry point ───────────────────────────────────────────────────
    graph.set_entry_point("classify")

    # ── Conditional routing from classify ─────────────────────────────
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "objection": "retrieve",       # Objections need RAG context
            "medical": "refusal",          # Medical → immediate refusal
            "proceed": "handoff",          # Ready → handoff
            "adversarial": "generate",     # Short template, no RAG needed
            "emotional": "generate",       # Emotional = acknowledge, no RAG
            "ambiguous": "generate",       # Clarify, no RAG needed
        },
    )

    # ── After RAG retrieval → generate response ──────────────────────
    graph.add_edge("retrieve", "generate")

    # ── After generation → quality gate ──────────────────────────────
    graph.add_edge("generate", "quality_gate")

    # ── Quality gate routing ─────────────────────────────────────────
    graph.add_conditional_edges(
        "quality_gate",
        route_after_quality,
        {
            "pass": END,            # Good response → send
            "warn": END,            # Acceptable → send with log
            "fail": "regenerate",   # Bad response → fix once
        },
    )

    # ── Regenerate → END (no infinite loops) ─────────────────────────
    graph.add_edge("regenerate", END)

    # ── Terminal nodes → END ─────────────────────────────────────────
    graph.add_edge("handoff", END)
    graph.add_edge("refusal", END)

    # ── Compile and return ───────────────────────────────────────────
    return graph.compile()


# Module-level compiled graph instance
trustycare_graph = build_trustycare_graph()
