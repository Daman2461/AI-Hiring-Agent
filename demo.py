import requests

url = "http://localhost:8000/find_candidates"
data = {
    "job_description": "Software Engineer, ML Research at Windsurf (Codeium) - Forbes AI 50 company building AI-powered developer tools. Looking for someone to train LLMs for code generation, $140-300k + equity, Mountain View.",
    "num_results": 10,
    "top_n": 5
}

response = requests.post(url, json=data)
print(response.json()) 