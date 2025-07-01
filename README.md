# Synapse AI Hiring Agent

A next-generation AI-powered sourcing agent for recruiters, built for the Synapse 25 AI Hackathon.

## 🚀 Features

- **LinkedIn Sourcing Agent:**  
  Paste a job description or job link, and discover top-matching LinkedIn candidates using Bing search, Selenium, and LLM-powered recruiter queries.
- **Rubric-Based Scoring:**  
  Each candidate is scored using a transparent rubric (education, trajectory, company, skills, location, tenure).
- **Personalized Outreach:**  
  Auto-generates tailored outreach messages for each candidate, highlighting their fit for the job.
- **AI Chat Assistant:**  
  Ask any hiring, resume, or job search question. Upload a resume for personalized, context-aware answers.
- **Modern UI:**  
  Beautiful Streamlit frontend for demo and real-world use.
- **FastAPI Backend:**  
  `/find_candidates` endpoint for programmatic access and HuggingFace Spaces deployment.

---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/synapse-ai-hiring-agent.git
cd synapse-ai-hiring-agent
```

### 2. Install Dependencies

We recommend using `conda` or `venv`:

```bash
# Using pip
pip install -r requirements.txt
```

Or, for conda:

```bash
conda create -n synapse python=3.10
conda activate synapse
pip install -r requirements.txt
```

### 3. Environment Variables

If using API keys (e.g., Mistral), create a `.env` file:

```
MISTRAL_API_KEY=your_mistral_api_key
```

### 4. Run the Streamlit App

```bash
streamlit run app.py
```

### 5. Run the FastAPI Backend

```bash
uvicorn main:app --reload
```

---

## 🌐 API Usage

### `/find_candidates` (POST)

**Input:**
```json
{
  "job_description": "Paste the job description here",
  "num_results": 10,
  "top_n": 7
}
```

**Output:**
```json
{
  "job_id": "backend-fintech-sf",
  "candidates_found": 25,
  "top_candidates": [
    {
      "name": "Jane Smith",
      "linkedin_url": "https://linkedin.com/in/janesmith",
      "fit_score": 8.5,
      "score_breakdown": {
        "education": 9.0,
        "trajectory": 8.0,
        "company": 8.5,
        "skills": 9.0,
        "location": 10.0,
        "tenure": 7.0
      },
      "outreach_message": "Hi Jane, I noticed your 6 years at Stripe and expertise in Python..."
    }
    // ...more candidates
  ]
}
```

---

## 🖥️ Demo

- Run the Streamlit app and try the "LinkedIn Sourcing Agent" and "AI Chat Assistant" features.
- For a video demo, see [demo.mp4](demo.mp4) (to be added).

---

## 🤖 Approach

- **Selenium + Bing:** For robust, CAPTCHA-free LinkedIn profile discovery.
- **LLM (Mistral):** For recruiter-style search queries, candidate scoring, and personalized outreach.
- **Modular Python:** Clean separation of scraping, scoring, messaging, and UI.
- **Scalable:** Ready for batch jobs, multi-source, and cloud deployment.

---

## ⚠️ Disclaimer

- This project is for educational/hackathon use only.
- Web scraping of LinkedIn is subject to their Terms of Service.

---

## 📄 License

MIT

---

## 🙏 Acknowledgements

- Synapse 25 AI Hackathon
- Mistral, Streamlit, Selenium, FastAPI, HuggingFace 