"""
Seed Content for SlayBot RAG Pipeline

Since slay.health is a React SPA that returns minimal content when scraped,
this file contains the authoritative content from the website, verified via
browser-rendered extraction and web research.

This serves as the ground truth for the RAG knowledge base.
"""

SEED_CONTENT = [
    # ──────────────────────────────────────────────────────────────
    # HOMEPAGE — Hero & Positioning
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Slay — Know Before You Say "I Do"

India's first AI-powered premarital health compatibility engine. 
Comprehensive health screening for couples — genetics, fertility, 
chronic health, and lifestyle screening. Starting at ₹799.

Slay helps couples understand their health compatibility before 
marriage. Whether it's an arranged marriage, love marriage, or you're 
planning a baby — Slay gives you the clarity you need to start your 
journey together with confidence.

The assessment is 100% private, doctor-reviewed, and designed for 
couples who want to be proactive about their future together.
""",
        "source_url": "https://slay.health/",
        "page_type": "homepage",
        "objection_tags": [],
        "emotional_tags": ["empowerment", "confidence"],
    },
    # ──────────────────────────────────────────────────────────────
    # HOW IT WORKS
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
How Slay Works — 3 Simple Steps:

Step 1: Choose Your Plan
Select the screening package that fits your needs. We have plans for 
arranged marriages, love marriages, and couples planning a baby.

Step 2: Get Screened
Visit a partner lab near you or get a home collection. Your samples are 
processed in NABL-accredited labs with the highest quality standards.

Step 3: Get Your Compatibility Report
Receive your private, doctor-reviewed health compatibility report. 
Understand your combined health picture across 6 key areas. If needed, 
speak with a Slay advisor for personalized guidance.

The entire process is private, simple, and designed to give you peace 
of mind — not anxiety.
""",
        "source_url": "https://slay.health/",
        "page_type": "how_it_works",
        "objection_tags": ["process_anxiety", "privacy"],
        "emotional_tags": ["reassurance", "simplicity"],
    },
    # ──────────────────────────────────────────────────────────────
    # 6-AREA COMPATIBILITY SCORING
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Slay Compatibility Score — 6 Key Areas:

1. Fertility Readiness (25%) — Reproductive health indicators for 
   both partners. Not a fertility diagnosis — a readiness snapshot.

2. Genetic Compatibility (25%) — Screens for conditions that run in 
   families. Identifies carrier status for things like thalassemia 
   and sickle cell — conditions where two carriers can have a child 
   with a serious health condition.

3. Chronic Health (20%) — Baseline checks for diabetes, thyroid, 
   heart health, and other long-term conditions that affect daily 
   life and family planning.

4. Infection Status (10%) — STI/STD screening including HIV, 
   Hepatitis B, HPV, and Herpes. Private, no judgment, just clarity.

5. Vitality Score (10%) — Nutrition, vitamin levels, and overall 
   energy markers. A snapshot of how healthy you are right now.

6. Lifestyle Alignment (10%) — Mental health baseline, stress 
   indicators, and lifestyle factors that affect long-term compatibility.

Total: 50+ health markers analyzed. Results reviewed by MDs.
""",
        "source_url": "https://slay.health/",
        "page_type": "assessment",
        "objection_tags": ["process_anxiety", "fear_of_results"],
        "emotional_tags": ["clarity", "empowerment"],
    },
    # ──────────────────────────────────────────────────────────────
    # PRICING
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Slay Pricing Plans:

Essential Plan — ₹799 per person
Advisory consultation with a Slay health expert. Understand what 
screening makes sense for your situation. No lab work — just guidance.

Compatibility Plan — ₹1,499 per couple (most popular)
Full health compatibility screening across all 6 areas. Includes 
lab work, AI-powered compatibility report, and advisor support.

Expert Plan — ₹2,499 per couple
Everything in Compatibility, plus a detailed doctor-reviewed report 
with genetic counselor consultation and personalized health roadmap.

All plans include: HIPAA-compliant data handling, private results 
(shared only with the couple), and advisor support.
""",
        "source_url": "https://slay.health/",
        "page_type": "pricing",
        "objection_tags": ["process_anxiety", "cost"],
        "emotional_tags": ["accessibility", "value"],
    },
    # ──────────────────────────────────────────────────────────────
    # PRIVACY & TRUST
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Privacy at Slay:

Your health data is yours. Period.

- Results are shared ONLY with the couple — not with families, 
  matchmakers, or any third party.
- All data is encrypted and HIPAA-compliant.
- You can delete your data at any time.
- We never sell or share your information.
- Reports are reviewed by licensed MDs before delivery.

Slay was built for people in sensitive life decisions. We know that 
privacy isn't a feature — it's a requirement. Your health story 
stays between you and your partner.
""",
        "source_url": "https://slay.health/",
        "page_type": "privacy",
        "objection_tags": ["privacy", "trust"],
        "emotional_tags": ["safety", "control"],
    },
    # ──────────────────────────────────────────────────────────────
    # TARGET AUDIENCES
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Who Uses Slay:

Arranged Marriage Couples — You're meeting someone your family found. 
You want to make sure you're compatible in every way — not just 
horoscopes. Slay helps you understand the health picture before 
you commit. Focus: hereditary risk, family health history, baseline 
chronic conditions, mental health.

Love Marriage Couples — You've been together, but medical records 
haven't come up. Slay gives you a safe, structured way to have the 
health conversation together. Focus: STI panels, reproductive health, 
genetic compatibility.

Planning a Baby — You're married or engaged and thinking about kids. 
Slay helps you understand your combined fertility readiness and 
genetic carrier status before you start trying.

Remarriage — Starting over and want to be more prepared this time. 
Slay gives you clarity without the awkwardness.

Concerned Parents — You want the best for your child's future. 
Slay gives you peace of mind that goes beyond the kundali.
""",
        "source_url": "https://slay.health/",
        "page_type": "audience",
        "objection_tags": ["relevance", "timing"],
        "emotional_tags": ["belonging", "normalization"],
    },
    # ──────────────────────────────────────────────────────────────
    # FAQ — COMMON QUESTIONS
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Frequently Asked Questions about Slay:

Q: Is this like a medical test?
A: It's a health screening — not a diagnosis. Think of it like a 
health compatibility check. We look at 50+ markers across 6 areas 
to give you a picture of your combined health. It's not about finding 
problems — it's about knowing your starting point together.

Q: Will my family see the results?
A: No. Results are shared ONLY with the couple. We never share with 
families, matchmakers, or anyone else. You decide what to share.

Q: What if we find something concerning?
A: That's actually the whole point — better to know now than after 
the wedding. If something comes up, a Slay advisor will walk you 
through what it means and what your options are. Most findings are 
manageable with the right planning.

Q: Is this only for arranged marriages?
A: No. Slay works for any couple — arranged, love, or mixed. The 
screening is the same. The conversation just starts differently.

Q: How long does it take?
A: The lab work takes about 30 minutes. Results are ready in 5-7 
business days. The advisor call is 20 minutes.

Q: What if my partner doesn't want to do this?
A: That's one of the most common situations we help with. Our 
advisors have helped hundreds of couples navigate this conversation. 
Sometimes it helps to frame it as something you're doing together, 
not something you're doing TO them.
""",
        "source_url": "https://slay.health/",
        "page_type": "faq",
        "objection_tags": ["process_anxiety", "privacy", "fear_of_results", "partner_resistance"],
        "emotional_tags": ["reassurance", "normalization", "empowerment"],
    },
    # ──────────────────────────────────────────────────────────────
    # SOCIAL PROOF & TRUST SIGNALS
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Slay Trust Signals:

- 2,847+ couples have used Slay
- 4.8/5 average rating from couples
- Reports reviewed by licensed MDs
- NABL-accredited partner labs
- HIPAA-compliant data handling
- Advisor team available for follow-up

Slay Technologies Pvt Ltd — Incorporated July 2025.
India's first AI-powered premarital health compatibility engine.
""",
        "source_url": "https://slay.health/",
        "page_type": "social_proof",
        "objection_tags": ["trust"],
        "emotional_tags": ["credibility", "safety"],
    },
    # ──────────────────────────────────────────────────────────────
    # OBJECTION HANDLING — ADVISOR TALKING POINTS
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Advisor Talking Points for Common Objections:

"My family will think something is wrong with me"
→ Families who care about kundali matching care about compatibility. 
Health compatibility is the same idea — just backed by science instead 
of stars. You're not saying something is wrong. You're saying you care 
enough to be thorough.

"We haven't even met properly yet, this feels too early"
→ Actually, this is the perfect time. Before emotional attachment makes 
it harder to have practical conversations. The earlier you know, the 
more choices you have.

"What if the results are bad?"
→ "Bad" results don't mean the match is over. Most findings are 
manageable. What's actually bad is finding out after the wedding, after 
kids, when the options are much harder. Knowing gives you power.

"This feels like I don't trust the other person"
→ It's not about trust — it's about care. You don't check the weather 
before a trip because you don't trust the sky. You check because you 
want to be prepared. This is the same thing.

"My parents will never agree to this"
→ Parents want the best for their child. Frame it as: "I want to be 
as thorough as possible — the way you taught me." Many parents actually 
appreciate it once they understand it's about preparation, not suspicion.

"I'd rather not know"
→ That's a very human feeling. But here's the thing — the health 
situation exists whether you test for it or not. Testing doesn't create 
problems. It reveals them early enough to plan for them.
""",
        "source_url": "https://slay.health/",
        "page_type": "advisor_guide",
        "objection_tags": [
            "family_pressure",
            "timing",
            "fear_of_results",
            "trust",
            "shame",
            "fatalism",
        ],
        "emotional_tags": [
            "shame",
            "fear",
            "pressure",
            "anxiety",
            "empowerment",
        ],
    },
    # ──────────────────────────────────────────────────────────────
    # CULTURAL CONTEXT — WHY THIS MATTERS
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Why Premarital Health Screening Matters in Arranged Marriage Contexts:

In arranged marriages, families invest enormous emotional and social 
capital in finding the right match. Horoscopes are checked. Backgrounds 
are verified. References are called. But health — the one thing that 
will affect every day of the couple's life together — is often left 
to chance.

This isn't because families don't care. It's because:
- Bringing up health feels like accusing the other family
- Health issues carry stigma that can "ruin" a match
- There's no cultural script for this conversation
- Izzat (family honor) makes vulnerability feel dangerous

Slay exists to be that cultural script. A neutral, private, structured 
way to have the health conversation — without it feeling like an 
accusation, a test, or a judgment.

Health compatibility is as important as horoscope compatibility. 
Maybe more — because unlike your kundali, your DNA actually determines 
what your children inherit.
""",
        "source_url": "https://slay.health/",
        "page_type": "cultural_context",
        "objection_tags": ["shame", "family_pressure", "cultural_resistance"],
        "emotional_tags": ["shame", "pressure", "normalization", "empowerment"],
    },
    # ──────────────────────────────────────────────────────────────
    # EMOTIONAL REFRAMES — CORE NARRATIVES
    # ──────────────────────────────────────────────────────────────
    {
        "content": """
Core Narrative Reframes for Slay:

1. FROM "This will hurt the match" TO "This protects the match"
   → The assessment doesn't create problems. It reveals information 
   that already exists. Knowing early means you can plan together.

2. FROM "This means I don't trust them" TO "This means I care about us"
   → Trust isn't about blind faith. It's about building a foundation 
   where both people feel safe and informed.

3. FROM "Something must be wrong with me" TO "I'm being responsible"
   → Taking a health screening is what responsible adults do before 
   making the biggest decision of their lives. It doesn't imply 
   anything is wrong.

4. FROM "My family will judge me" TO "My family would want this for me"
   → Families who check kundali, background, and finances — they're 
   already doing compatibility checks. Health is just the one they 
   haven't thought of yet.

5. FROM "I'd rather not know" TO "Knowing gives me choices"
   → The health situation exists whether you test or not. But knowing 
   gives you the power to plan, prepare, and protect your future family.

6. FROM "This is too early" TO "This is actually the perfect time"
   → Before emotional attachment, before commitments are made, before 
   families are deeply invested — this is when the conversation is 
   easiest and most empowering.
""",
        "source_url": "https://slay.health/",
        "page_type": "reframes",
        "objection_tags": [
            "shame",
            "trust",
            "family_pressure",
            "fatalism",
            "timing",
            "fear_of_results",
        ],
        "emotional_tags": [
            "empowerment",
            "reframe",
            "normalization",
        ],
    },
]
