"""
TrustyBot Evaluation Harness

Runs all 15 test cases through the /chat endpoint, evaluates each response
using the LLM-as-judge system, and produces an aggregated eval report.

Usage:
    python eval/harness.py

Requirements:
    - Backend server running at http://localhost:8000
    - GROQ_API_KEY set in .env
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

import httpx

# Add parent dir for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.judge import score_response, check_must_not_contain


# ── Configuration ────────────────────────────────────────────────────────

API_URL = "http://localhost:8000/chat"
TEST_CASES_PATH = Path(__file__).resolve().parent / "test_cases.json"
RESULTS_OUTPUT_PATH = Path(__file__).resolve().parent / "eval_results.json"
PASS_THRESHOLD = 82


# ── Test Runner ──────────────────────────────────────────────────────────

def run_test_case(test_case: dict) -> dict:
    """
    Run a single test case through the API and evaluate the response.
    """
    test_id = test_case["id"]
    user_input = test_case["input"]

    print(f"\n{'─' * 50}")
    print(f"🧪 {test_id}: {test_case['category']}")
    print(f"   Input: \"{user_input[:80]}...\"" if len(user_input) > 80 else f"   Input: \"{user_input}\"")

    # Step 1: Call the chat API
    try:
        response = httpx.post(
            API_URL,
            json={
                "message": user_input,
                "conversation_id": f"eval-{test_id}",
                "conversation_history": [],
            },
            timeout=30,
        )
        response.raise_for_status()
        api_result = response.json()
        bot_response = api_result.get("response", "")
        detected_category = api_result.get("category", "unknown")

    except httpx.ConnectError:
        print("   ✗ Cannot connect to API. Is the server running?")
        return {
            "test_id": test_id,
            "status": "error",
            "error": "Cannot connect to API server",
            "score": 0,
            "pass": False,
        }

    except Exception as e:
        print(f"   ✗ API error: {e}")
        return {
            "test_id": test_id,
            "status": "error",
            "error": str(e),
            "score": 0,
            "pass": False,
        }

    print(f"   Response: \"{bot_response[:100]}...\"" if len(bot_response) > 100 else f"   Response: \"{bot_response}\"")
    print(f"   Category: {detected_category} (expected: {test_case['expected_category']})")

    # Step 2: Check must_not_contain violations
    must_not_violations = check_must_not_contain(
        bot_response,
        test_case.get("must_not_contain", []),
    )

    # Step 3: LLM-as-judge evaluation
    eval_result = score_response(
        objection_category=test_case["category"],
        user_message=user_input,
        chatbot_response=bot_response,
        conversation_context="No prior context (first message in evaluation).",
    )

    # Step 4: Apply hard failures for must_not_contain
    if must_not_violations:
        eval_result["hard_failure"] = True
        eval_result["hard_failure_reason"] = "; ".join(must_not_violations)
        eval_result["total_score"] = 0
        eval_result["pass"] = False

    # Step 5: Check against threshold
    threshold = test_case.get("pass_threshold", PASS_THRESHOLD)
    passed = eval_result["total_score"] >= threshold and not eval_result.get("hard_failure", False)
    eval_result["pass"] = passed

    # Step 6: Category accuracy check
    category_match = detected_category == test_case["expected_category"]

    # Print result
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"   Score: {eval_result['total_score']}/100 (threshold: {threshold}) — {status}")
    if eval_result.get("worst_aspect"):
        print(f"   Worst: {eval_result['worst_aspect']}")
    if must_not_violations:
        print(f"   🚫 Violations: {must_not_violations}")

    # Throttle API calls to avoid rate limiting
    time.sleep(2)

    return {
        "test_id": test_id,
        "category": test_case["category"],
        "input": user_input,
        "response": bot_response,
        "detected_category": detected_category,
        "expected_category": test_case["expected_category"],
        "category_match": category_match,
        "score": eval_result["total_score"],
        "breakdown": eval_result.get("breakdown", {}),
        "hard_failure": eval_result.get("hard_failure", False),
        "hard_failure_reason": eval_result.get("hard_failure_reason"),
        "pass": passed,
        "threshold": threshold,
        "worst_aspect": eval_result.get("worst_aspect"),
        "improvement": eval_result.get("improvement"),
        "must_not_violations": must_not_violations,
        "status": "completed",
    }


# ── Aggregation ──────────────────────────────────────────────────────────

def aggregate_results(results: list[dict]) -> dict:
    """Aggregate individual test results into a summary report."""
    completed = [r for r in results if r["status"] == "completed"]
    errors = [r for r in results if r["status"] == "error"]

    if not completed:
        return {"error": "No tests completed successfully"}

    total_pass = sum(1 for r in completed if r["pass"])
    total_fail = sum(1 for r in completed if not r["pass"])
    avg_score = sum(r["score"] for r in completed) / len(completed)
    category_matches = sum(1 for r in completed if r.get("category_match", False))

    # Per-category breakdown
    categories = {}
    for r in completed:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"tests": 0, "passed": 0, "scores": []}
        categories[cat]["tests"] += 1
        categories[cat]["scores"].append(r["score"])
        if r["pass"]:
            categories[cat]["passed"] += 1

    for cat in categories:
        scores = categories[cat]["scores"]
        categories[cat]["avg_score"] = sum(scores) / len(scores) if scores else 0
        categories[cat]["pass_rate"] = (
            f"{categories[cat]['passed']}/{categories[cat]['tests']}"
        )
        del categories[cat]["scores"]

    # Worst performing test
    worst = min(completed, key=lambda x: x["score"])

    return {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(results),
        "completed": len(completed),
        "errors": len(errors),
        "passed": total_pass,
        "failed": total_fail,
        "pass_rate": f"{total_pass}/{len(completed)} ({100 * total_pass / len(completed):.0f}%)",
        "average_score": round(avg_score, 1),
        "category_accuracy": f"{category_matches}/{len(completed)} ({100 * category_matches / len(completed):.0f}%)",
        "by_category": categories,
        "worst_test": {
            "id": worst["test_id"],
            "score": worst["score"],
            "input": worst["input"][:80],
            "worst_aspect": worst.get("worst_aspect"),
        },
        "individual_results": results,
    }


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🧪 TrustyBot Evaluation Harness")
    print(f"   Threshold: {PASS_THRESHOLD}/100")
    print(f"   API: {API_URL}")
    print("=" * 60)

    # Load test cases
    with open(TEST_CASES_PATH, "r") as f:
        test_cases = json.load(f)

    print(f"\n📋 Loaded {len(test_cases)} test cases\n")

    # Run all tests
    results = []
    for tc in test_cases:
        result = run_test_case(tc)
        results.append(result)

    # Aggregate
    summary = aggregate_results(results)

    # Save results
    with open(RESULTS_OUTPUT_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n💾 Results saved to {RESULTS_OUTPUT_PATH}")

    # Print summary table
    print("\n" + "=" * 60)
    print("📊 EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  Total tests:      {summary.get('total_tests', 0)}")
    print(f"  Completed:        {summary.get('completed', 0)}")
    print(f"  Pass rate:        {summary.get('pass_rate', 'N/A')}")
    print(f"  Average score:    {summary.get('average_score', 0)}/100")
    print(f"  Category accuracy: {summary.get('category_accuracy', 'N/A')}")

    print(f"\n  📂 By Category:")
    for cat, data in summary.get("by_category", {}).items():
        print(f"    {cat:25s} — Pass: {data['pass_rate']:5s}  Avg: {data['avg_score']:.0f}")

    worst = summary.get("worst_test", {})
    if worst:
        print(f"\n  ⚠ Worst: {worst.get('id', '?')} (score: {worst.get('score', 0)})")
        print(f"    → {worst.get('worst_aspect', 'N/A')}")

    print("\n" + "=" * 60)

    # Exit code for CI
    pass_rate = summary.get("passed", 0) / max(summary.get("completed", 1), 1)
    sys.exit(0 if pass_rate >= 0.8 else 1)


if __name__ == "__main__":
    main()
