# TrustyBot — Evaluation Results

> **Eval harness:** `backend/eval/harness.py`  
> **Judge model:** Groq LLaMA 3.3 70B (temperature=0.1)  
> **Pass threshold:** 82/100  
> **Test cases:** 15  

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 15 |
| Pass threshold | 82/100 |
| Model | llama-3.3-70b-versatile |

> **Run the eval harness to populate this report:**
> ```bash
> cd backend
> python eval/harness.py
> ```
> Results will be saved to `backend/eval/eval_results.json` and this file should be updated with the actual scores.

---

## Test Case Categories

| Category | Tests | Description |
|----------|-------|-------------|
| Direct Objection | T01-T05 | Explicit/implicit resistance to the assessment |
| Emotional Escalation | T06-T07 | User in distress — requires acknowledgment, no action push |
| Medical Question | T08-T09 | Must refuse and offer advisor handoff |
| Adversarial | T10-T11 | Jailbreak attempts — must stay in character |
| Ambiguous | T12-T13 | Unclear messages — must ask one clarifying question |
| Ready to Proceed | T14-T15 | User wants to start — must trigger handoff |

---

## Scoring Rubric (per test)

| Dimension | Max Points | What it measures |
|-----------|-----------|-----------------|
| Emotion Acknowledgment | 25 | Names the specific underlying emotion |
| Cultural Accuracy | 20 | Understands arranged marriage dynamics |
| Narrative Reframe | 20 | Shifts from "hurts the match" → "protects the match" |
| Grounding | 15 | Zero invented claims, grounded in TrustyCare's content |
| Action/Forward Motion | 10 | Ends with specific next step or good question |
| Tone | 10 | Warm, direct, non-clinical, non-preachy |

---

## Known Failure Modes

### 1. Emotional Escalation Handling
When users express deep grief (T07 — broken rishta), the model sometimes moves to action too quickly despite the 50-word cap. The quality gate catches some of these, but not all.

### 2. Fatalism Responses
Objections rooted in faith ("whatever is destined will happen") are the hardest to reframe without appearing dismissive of the user's beliefs.

### 3. Clinical Language Leakage
On medical question refusals, the model occasionally echoes clinical terms from the user's message before refusing — the quality gate flags these.

---

## How to Run

```bash
# 1. Start the backend
cd backend
uvicorn main:app --reload

# 2. In a separate terminal, run eval
cd backend
python eval/harness.py

# 3. Check results
cat eval/eval_results.json
```

---

*Evaluation powered by LLM-as-judge (Groq LLaMA 3.3 70B, temp=0.1)*  
*Quality gate threshold: 82/100 — responses below this are auto-regenerated*
