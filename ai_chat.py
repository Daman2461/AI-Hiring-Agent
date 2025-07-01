import os
from typing import Optional
import requests
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"  # Update if using a different provider

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = (
    "You are an expert AI assistant for hiring. "
    "Answer questions about the candidate based only on the provided resume. "
    "Give a direct, relevant answer to the question that is clear and informative, but not overly detailed or verbose. Keep the answer focused and of moderate length."
)


def answer_question(context: str, question: str) -> Optional[str]:
    if not context or not question:
        return None
    data = {
        "model": "mistral-medium",  # or mistral-small, mistral-large, etc.
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Resume: {context}\n\nQuestion: {question}"}
        ],
        "max_tokens": 1024,
        "temperature": 0.2
    }
    try:
        response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e}" 