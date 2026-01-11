# ai_responder.py

import openai
from config import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE, BOT_NAME

openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = f"""
You are {BOT_NAME}, a witty anime-style character.
You roast people in a funny, friendly, clever way.
No abuse, no hate, no profanity.
Replies must be short, sarcastic, and humorous.
"""

def generate_roast(chat_history):
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": chat_history}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )

        return response.choices[0].message["content"].strip()

    except Exception as e:
        return "Believe it! My brain just lagged like a Genin on low chakra 😅"
