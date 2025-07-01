import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
from urllib.parse import quote, parse_qs, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

def extract_search_terms(job_description):
    # Simple heuristics for demo; can be replaced with NLP for production
    import re
    # Extract title (first line or before 'at')
    title = ''
    lines = job_description.split('\n')
    if lines:
        title = lines[0]
    if ' at ' in title:
        title = title.split(' at ')[0]
    # Extract location (look for common city/state/country patterns)
    location = ''
    loc_match = re.search(r'in ([A-Za-z ,]+)', job_description)
    if loc_match:
        location = loc_match.group(1).strip()
    # Extract skills (look for keywords)
    skills = []
    skill_keywords = [
        'machine learning', 'ml', 'deep learning', 'ai', 'python', 'llm', 'nlp', 'data',
        'backend', 'frontend', 'cloud', 'aws', 'gcp', 'azure', 'react', 'node', 'django', 'flask', 'pytorch', 'tensorflow', 'kubernetes', 'docker'
    ]
    for kw in skill_keywords:
        if kw.lower() in job_description.lower():
            skills.append(kw)
    # Build query
    query = f'site:linkedin.com/in "{title.strip()}"'
    for skill in skills:
        query += f' "{skill}"'
    if location:
        query += f' "{location}"'
    return query

def generate_search_query_with_mistral(job_description):
    """
    Use Mistral to generate a recruiter-style Google search query for LinkedIn profiles,
    using only the most relevant job title, skills, and location from the job description.
    Do NOT include the company name. Output ONLY the search query string, nothing else.
    """
    system_prompt = (
        "You are an expert technical sourcer. "
        "Given the following job description, generate a Google search query for LinkedIn profiles. "
        "The query should use only the most relevant job title, skills, and location, and must NOT include the company name. "
        "Format the query for Google search, starting with site:linkedin.com/in, and use double quotes for exact matches. "
        "Output ONLY the search query string, nothing else."
    )
    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": job_description}
        ],
        "max_tokens": 128,
        "temperature": 0.2
    }
    try:
        response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        query = result["choices"][0]["message"]["content"].strip()
        # Basic sanity check
        if query.lower().startswith("site:linkedin.com/in"):
            return query
    except Exception as e:
        print(f"[WARN] Mistral search query generation failed: {e}")
    # Fallback to heuristic
    return extract_search_terms(job_description)

def search_linkedin(job_description, num_results=10):
    query = generate_search_query_with_mistral(job_description)
    candidates = []
    page = 1
    max_pages = 3
    while len(candidates) < num_results and page <= max_pages:
        first = (page - 1) * 10 + 1
        url = f'https://www.bing.com/search?q={quote(query)}&count=10&first={first}'
        print(f"[DEBUG] Bing Search Query: {query} (page {page})")
        print(f"[DEBUG] Bing Search URL: {url}")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(2)
        # Debug: print the page source to a file for inspection
        with open(f'bing_search_debug_page{page}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"[DEBUG] Saved Bing search page source to bing_search_debug_page{page}.html")
        links = driver.find_elements(By.XPATH, '//li[@class="b_algo"]//h2/a[contains(@href, "linkedin.com/in")]')
        for link in links:
            href = link.get_attribute('href')
            if href and 'linkedin.com/in' in href:
                title = link.text.strip()
                try:
                    parent = link.find_element(By.XPATH, './ancestor::li[@class="b_algo"]')
                    snippet = parent.text.strip()
                except Exception:
                    snippet = ''
                # Trim snippet for UI
                short_snippet = snippet.split('\n')[0][:120] + ('...' if len(snippet.split('\n')[0]) > 120 else '')
                candidates.append({
                    "name": title,
                    "linkedin_url": href,
                    "headline": short_snippet,
                    "full_headline": snippet
                })
            if len(candidates) >= num_results:
                break
        driver.quit()
        page += 1
    print(f"[DEBUG] Parsed candidates: {candidates}")
    return candidates[:num_results]

def score_candidate(candidate, job_description):
    system_prompt = (
        "You are an expert recruiter. Given the candidate's LinkedIn headline and the job description, "
        "score the candidate from 1.0 to 10.0 for fit (allow decimals). "
        "Provide a JSON object ONLY with 'score' (float) and a 'breakdown' (floats) for education, trajectory, company, skills, location, tenure. "
        "All values should be floats between 1.0 and 10.0. Output ONLY the JSON, no extra text. Example: {\"score\": 8.7, \"breakdown\": {\"education\": 9.0, ...}}"
    )
    user_content = f"Candidate: {candidate}\nJob Description: {job_description}"
    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "max_tokens": 256,
        "temperature": 0.2
    }
    import json, re
    try:
        response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()
        try:
            score_data = json.loads(content)
            # Normalize LinkedIn URL
            if 'linkedin_url' in candidate and not candidate['linkedin_url'].startswith('http'):
                candidate['linkedin_url'] = 'https://' + candidate['linkedin_url'].lstrip('/')
            # Ensure floats
            score = float(score_data.get('score', 0))
            breakdown = {k: float(v) for k, v in score_data.get('breakdown', {}).items()}
            return {"score": score, "breakdown": breakdown}
        except Exception as e:
            print(f"[WARN] Mistral did not return valid JSON. Raw response: {content}")
            # Fallback: try to extract score and breakdown with regex
            score_match = re.search(r'"score"\s*:\s*([0-9]+\.?[0-9]*)', content)
            score = float(score_match.group(1)) if score_match else 0.0
            breakdown = {}
            breakdown_match = re.search(r'"breakdown"\s*:\s*\{([^}]*)\}', content)
            if breakdown_match:
                for item in breakdown_match.group(1).split(','):
                    k_v = item.split(':')
                    if len(k_v) == 2:
                        k = k_v[0].replace('"', '').strip()
                        v = re.sub(r'[^0-9.]', '', k_v[1])
                        try:
                            breakdown[k] = float(v)
                        except:
                            pass
            return {"score": score, "breakdown": breakdown}
    except Exception as e:
        print(f"Error scoring candidate: {e}")
        return {"score": 0.0, "breakdown": {}}

def generate_outreach(candidate, job_description):
    system_prompt = (
        "You are an expert recruiter. Write a personalized LinkedIn outreach message for the candidate, "
        "referencing their profile and how it matches the job. Keep it professional and concise."
    )
    user_content = f"Candidate: {candidate}\nJob Description: {job_description}"
    data = {
        "model": "mistral-medium",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "max_tokens": 256,
        "temperature": 0.5
    }
    response = requests.post(MISTRAL_API_URL, headers=HEADERS, json=data, timeout=30)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

def agent_pipeline(job_description, num_results=10, top_n=10):
    candidates = search_linkedin(job_description, num_results)
    scored = []
    for c in candidates:
        score_data = score_candidate(c, job_description)
        c["fit_score"] = score_data.get("score", 0)
        c["score_breakdown"] = score_data.get("breakdown", {})
        scored.append(c)
    scored = sorted(scored, key=lambda x: x["fit_score"], reverse=True)[:top_n]
    for c in scored:
        c["outreach_message"] = generate_outreach(c, job_description)
    return {
        "job_id": job_description[:30].replace(" ", "-").lower(),
        "candidates_found": len(candidates),
        "top_candidates": scored
    } 