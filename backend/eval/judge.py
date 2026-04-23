"""
LLM-as-Judge Scoring System for TrustyBot

Uses a separate Groq call with the EVALUATOR_SYSTEM_PROMPT to score
chatbot responses on a 0-100 rubric. Designed to be strict and
calibrated — looking for failures, not successes.
"""

import json
import os

from groq import Groq
from dotenv import load_dotenv

from agent.prompts import (
    EVALUATOR_SYSTEM_PROMPT,
    EVALUATOR_USER_PROMPT,
    GROQ_EVALUATOR_CONFIG,
)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def score_response(
    objection_category: str,
    user_message: str,
    chatbot_response: str,
    conversation_context: str = "No prior context.",
) -> dict:
    """
    Score a chatbot response using the LLM-as-judge evaluator.
    
    Args:
        objection_category: The test case category (e.g., "direct_objection")
        user_message: The user's input message
        chatbot_response: The chatbot's response to evaluate
        conversation_context: Any conversation history context
        
    Returns:
        Dict with scoring breakdown, pass/fail, and improvement suggestions.
    """
    user_prompt = EVALUATOR_USER_PROMPT.format(
        objection_category=objection_category,
        user_message=user_message,
        chatbot_response=chatbot_response,
        conversation_context=conversation_context,
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            **GROQ_EVALUATOR_CONFIG,
        )

        result = response.choices[0].message.content.strip()
        parsed = json.loads(result)

        # Ensure all expected fields exist
        return {
            "total_score": parsed.get("total_score", 0),
            "breakdown": parsed.get("breakdown", {
                "emotion_acknowledgment": 0,
                "cultural_accuracy": 0,
                "narrative_reframe": 0,
                "grounding": 0,
                "action": 0,
                "tone": 0,
            }),
            "hard_failure": parsed.get("hard_failure", False),
            "hard_failure_reason": parsed.get("hard_failure_reason"),
            "pass": parsed.get("pass", False),
            "worst_aspect": parsed.get("worst_aspect", "Unknown"),
            "improvement": parsed.get("improvement", "No suggestion"),
        }

    except json.JSONDecodeError:
        return {
            "total_score": 0,
            "breakdown": {},
            "hard_failure": True,
            "hard_failure_reason": "Evaluator returned invalid JSON",
            "pass": False,
            "worst_aspect": "Evaluation failed",
            "improvement": "Check evaluator prompt",
        }

    except Exception as e:
        return {
            "total_score": 0,
            "breakdown": {},
            "hard_failure": True,
            "hard_failure_reason": f"Evaluator error: {str(e)}",
            "pass": False,
            "worst_aspect": "Evaluation failed",
            "improvement": "Check API connection",
        }


def check_must_not_contain(response: str, forbidden: list[str]) -> list[str]:
    """Check if response contains any forbidden phrases."""
    violations = []
    response_lower = response.lower()
    for phrase in forbidden:
        if phrase.lower() in response_lower:
            violations.append(f"Contains forbidden phrase: '{phrase}'")
    return violations
