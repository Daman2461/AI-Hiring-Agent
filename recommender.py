import os
import requests
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = (
    "You are an expert technical recruiter. "
    "Given the following candidate's parsed resume data, provide a single integer score from 0 to 100 representing their suitability for a generic software engineering role. "
    "Only output the integer score, with no explanation or extra text."
)

def score_candidate(parsed: dict) -> int:
    resume_summary = str(parsed)
    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Candidate data: {resume_summary}"}
        ],
        "max_tokens": 10,
        "temperature": 0.2
    }
    try:
        response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        score_str = result["choices"][0]["message"]["content"].strip()
        # Extract integer from response
        score = int(''.join(filter(str.isdigit, score_str)))
        return score
    except Exception as e:
        print(f"Error scoring candidate: {e}")
        return 0 