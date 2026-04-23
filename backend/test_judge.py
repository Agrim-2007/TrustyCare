import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval.judge import score_response

print("Testing evaluator...")
result = score_response(
    objection_category="direct_objection",
    user_message="If I bring this up, his family will think something is wrong with me.",
    chatbot_response="I understand you're feeling ashamed. But this will protect the match.",
    conversation_context="No prior context."
)
print("Result dictionary:")
print(result)

# Let's also do a direct groq call to see the raw text
from groq import Groq
from eval.judge import EVALUATOR_SYSTEM_PROMPT, EVALUATOR_USER_PROMPT, GROQ_EVALUATOR_CONFIG
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
user_prompt = EVALUATOR_USER_PROMPT.format(
    objection_category="direct_objection",
    user_message="If I bring this up, his family will think something is wrong with me.",
    chatbot_response="I understand you're feeling ashamed. But this will protect the match.",
    conversation_context="No prior context."
)
response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ],
    **GROQ_EVALUATOR_CONFIG,
)
print("\nRaw LLM output:")
print(response.choices[0].message.content)
