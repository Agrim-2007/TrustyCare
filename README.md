# TrustyBot — Objection Handling Agent for TrustyCare

> Pre-marriage health assessment companion — warm, direct, culturally fluent.  
> Stack: FastAPI + LangGraph + Groq + React + FAISS

---

## 🎯 What This Is

TrustyBot is an AI-powered objection-handling chatbot for **TrustyCare** — India's first pre-marriage health compatibility platform. It helps people navigate the emotionally charged decision of whether to take a health screening before an arranged marriage.

**The core insight:** When someone objects to pre-marriage health screening, they're not asking "is this safe?" — they're asking **"will doing this cost me the marriage?"**

TrustyBot handles objections with:
- **Emotional intelligence** — names the real feeling, not the surface question
- **Cultural fluency** — understands izzat, family pressure, kundali matching
- **Narrative reframing** — shifts from "this hurts the match" to "this protects the match"
- **Strict guardrails** — refuses medical questions, catches adversarial attempts, quality-gates every response

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                  │
│              Full-screen conversational UI                │
│         Fraunces + DM Sans · Warm ivory palette          │
└──────────────────────┬──────────────────────────────────┘
                       │ POST /chat
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                         │
│                                                           │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌───────┐ │
│  │Classify │──▸│ Retrieve  │──▸│ Generate │──▸│Quality│ │
│  │ (LLM)   │   │  (FAISS)  │   │  (LLM)   │   │ Gate  │ │
│  └────┬────┘   └──────────┘   └──────────┘   └───┬───┘ │
│       │                                           │      │
│       ├── medical ──▸ REFUSAL + Advisor Handoff    │      │
│       ├── proceed ──▸ HANDOFF Trigger              │      │
│       └── adversarial ──▸ DECLINE Template         │      │
│                                                    │      │
│                              fail ◀───────────────┘      │
│                                │                          │
│                          ┌─────▼─────┐                   │
│                          │ Regenerate │──▸ END            │
│                          └───────────┘                    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Eval Harness: 15 test cases · LLM-as-judge      │    │
│  │ Pass threshold: 82/100 · Auto-regen on fail      │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Setup (< 10 minutes)

### Prerequisites
- Python 3.11+
- Node 18+
- Groq API key ([free tier](https://console.groq.com))

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # macOS/Linux
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Build the RAG knowledge base
python rag/ingest.py

# Start the server
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — you'll see TrustyBot ready to chat.

---

## 📂 Project Structure

```
trustycare/
├── frontend/                  # React (Vite) — full-screen chat UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx      # Message list + welcome state
│   │   │   ├── MessageBubble.jsx   # Bot/user/refusal bubbles
│   │   │   ├── TypingIndicator.jsx # 3-dot pulse animation
│   │   │   └── HandoffCard.jsx     # Advisor booking CTA
│   │   ├── hooks/
│   │   │   └── useChat.js          # Chat state + API calls
│   │   ├── App.jsx                 # Main layout + input bar
│   │   ├── index.css               # Design system
│   │   └── main.jsx                # Entry point
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── backend/                   # FastAPI + LangGraph
│   ├── main.py                # API server + /chat endpoint
│   ├── agent/
│   │   ├── graph.py           # LangGraph state machine
│   │   ├── nodes.py           # All node functions
│   │   ├── state.py           # TrustyCareState TypedDict
│   │   └── prompts.py         # All prompts + Groq configs
│   ├── rag/
│   │   ├── ingest.py          # Scraper + chunker + embedder
│   │   ├── retriever.py       # FAISS similarity search
│   │   ├── seed_content.py    # Authoritative TrustyCare content
│   │   └── vectorstore/       # Persisted FAISS index
│   ├── eval/
│   │   ├── harness.py         # 15-test evaluation runner
│   │   ├── judge.py           # LLM-as-judge scoring
│   │   └── test_cases.json    # Test case definitions
│   ├── requirements.txt
│   └── .env.example
│
├── docs/
│   ├── OBJECTIONS_100.md      # All 100 objections brainstormed
│   ├── OBJECTIONS_30.md       # Shortlisted 30 with rationale
│   ├── OBJECTIONS.md          # Final top 10 (deliverable)
│   └── EVAL_RESULTS.md        # Evaluation report
│
└── README.md
```

---

## 🧠 Design Decisions

### Why LangGraph over LangChain?
LangGraph gives us a proper state machine with conditional routing — critical for correctly handling the `classify → retrieve → generate → quality_gate` loop. LangChain runnable chains would have required more glue code for the same behavior. The graph also makes the decision tree (medical → refusal, proceed → handoff) declarative and visible.

### Why RAG + Prompt together?
- **Prompt alone:** High risk of tone drift and invented claims
- **RAG alone:** Retrieval can miss the emotional dimension
- **Together:** RAG grounds the facts, prompt guides the emotional register

### Why not fine-tune?
Overkill at this scope. The eval-and-regen loop (quality gate) gives us similar quality improvement at zero training cost. The self-check catches most violations and the regeneration prompt fixes them.

### Why Groq (LLaMA 3.3 70B)?
Free tier, sub-second latency, strong instruction following. Sufficient for structured output (classification, JSON responses). Temperature tuned per use case: 0.0 for classification, 0.1 for evaluation, 0.4 for generation.

### Why FAISS over ChromaDB?
Simpler deployment (single file persistence), faster similarity search, no server dependency. At this content volume (~50 chunks), FAISS IndexFlatIP is optimal.

---

## 🧪 Evaluation

### Running the eval harness

```bash
# Make sure backend is running first
cd backend
python eval/harness.py
```

### 15 Test Cases

| Category | Tests | Threshold |
|----------|-------|-----------|
| Direct Objection | 5 | 82/100 |
| Emotional Escalation | 2 | 82/100 |
| Medical Question | 2 | 95/100 |
| Adversarial | 2 | 95/100 |
| Ambiguous | 2 | 82/100 |
| Ready to Proceed | 2 | 90/100 |

### Scoring Rubric (100 points)
- Emotion Acknowledgment: 25 pts
- Cultural Accuracy: 20 pts
- Narrative Reframe: 20 pts
- Grounding: 15 pts
- Action/Forward Motion: 10 pts
- Tone: 10 pts

### Self-Improvement Loop
If the quality gate scores a response below 82, it automatically regenerates with the failure context. Max 1 regeneration to prevent infinite loops.

---

## ⚠️ Worst Failure Mode

**Emotional escalation handling.** When users express deep grief about a past broken match (T07), the model sometimes moves to action too quickly. The 50-word cap helps but doesn't fully solve this — a production version needs a dedicated emotional support path, possibly with a human-in-loop trigger at grief keywords.

---

## 🔮 If I Had Another Week

1. Fine-tune evaluator on 200 human-labeled examples
2. Add conversation memory (Redis) for multi-session continuity
3. Build advisor dashboard showing handoff requests in real-time
4. Add language detection + Hinglish response mode
5. A/B test 2 reframe strategies per objection
6. Streaming responses (SSE) for real-time typing feel
7. Voice input support for mobile users
8. Add more testing layers

---

## 📊 Objection Pipeline

The objection library was developed through a structured research process:

1. **100 objections** brainstormed across 8 psychological dimensions → [OBJECTIONS_100.md](docs/OBJECTIONS_100.md)
2. **30 shortlisted** based on frequency, emotional depth, uniqueness, cultural specificity, testability → [OBJECTIONS_30.md](docs/OBJECTIONS_30.md)  
3. **10 final** covering 7/8 dimensions, each with distinct reframe strategy → [OBJECTIONS.md](docs/OBJECTIONS.md)

---

*Built for TrustyCare Technologies Pvt Ltd — LLM Intern Assignment*  
*Author: Agrim | Stack: FastAPI + LangGraph + Groq + React + FAISS*
