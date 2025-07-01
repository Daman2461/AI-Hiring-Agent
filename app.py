import streamlit as st
import os
from resume_parser import extract_info
from ai_chat import answer_question
from recommender import score_candidate
from linkedin_agent import agent_pipeline

st.set_page_config(page_title="AI Hiring Agent", layout="centered")
st.markdown("""
<style>
    .main {background-color: #f8fafc;}
    .stButton>button {background-color: #2563eb; color: white; font-weight: 600; border-radius: 6px;}
    .stTextInput>div>div>input, .stTextArea>div>textarea {border-radius: 6px;}
    .stNumberInput>div>input {border-radius: 6px;}
    .stMarkdown h2 {color: #2563eb;}
    .stMarkdown h3 {color: #2563eb;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Synapse AI Hiring Agent")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["LinkedIn Sourcing Agent", "AI Chat Assistant"])

def is_hf_space():
    return os.environ.get("HF_SPACE") == "1" or "appuser" in os.path.expanduser("~")

if is_hf_space():
    st.title("Synapse AI Hiring Agent API Demo (Streamlit)")
    st.write("Paste a job description below to get the top 10 LinkedIn candidates and personalized outreach messages.")
    job_desc = st.text_area("Job Description", height=200)
    if st.button("Find Candidates") and job_desc.strip():
        with st.spinner("Searching..."):
            result = agent_pipeline(job_desc, num_results=10, top_n=10)
            st.json(result)
else:
    if page == "LinkedIn Sourcing Agent":
        st.header("🕵️‍♂️ LinkedIn Sourcing Agent")
        st.write("Paste a job description or a job post link, and we'll fetch top LinkedIn candidates based on fit.")

        job_link = st.text_input("🔗 Paste job post link (optional):")
        job_desc_input = st.text_area("📋 Or paste the job description manually:", height=150)
        fetch_clicked = st.button("📥 Fetch from Link")

        if fetch_clicked and job_link.strip():
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from webdriver_manager.chrome import ChromeDriverManager
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=chrome_options)
                driver.get(job_link.strip())
                import time
                time.sleep(3)  # Wait for JS to render
                try:
                    body = driver.find_element('tag name', 'body')
                    desc = body.get_attribute('innerText').strip()
                except Exception:
                    desc = ''
                driver.quit()
                if desc:
                    st.session_state['job_desc_from_link'] = desc
                    st.success("✅ All visible text from the page fetched as job description!")
                else:
                    st.warning("⚠️ Could not extract any text from this page.")
            except Exception as e:
                st.error(f"❌ Error fetching job description: {e}")

        # Preload fetched JD if available
        if 'job_desc_from_link' in st.session_state:
            with st.expander("📄 Fetched Job Description", expanded=True):
                st.text_area("Fetched Content:", value=st.session_state['job_desc_from_link'], height=200, disabled=True)
            job_desc_input = st.session_state['job_desc_from_link']

        # Candidate sourcing form
        with st.form("sourcing_form"):
            st.markdown("---")
            st.markdown("### ✏️ Finalize Job Description Input")
            final_jd = st.text_area("Job Description to Use:", value=job_desc_input, height=180)
            num_results = st.number_input("How many candidates to find?", 1, 20, value=10)
            top_n = st.number_input("How many top candidates to show?", 1, 20, value=5)
            submitted = st.form_submit_button("🔍 Find Candidates")

        if submitted and final_jd.strip():
            with st.spinner("Searching candidates on LinkedIn (via Bing)..."):
                try:
                    import requests
                    resp = requests.post(
                        "http://localhost:8000/find_candidates",
                        json={"job_description": final_jd, "num_results": num_results, "top_n": top_n},
                        timeout=120
                    )
                    data = resp.json()
                    candidates = data.get("top_candidates", [])

                    if not candidates:
                        st.warning("⚠️ No strong candidates found. Try editing the job description.")
                    else:
                        st.success(f"✅ Found {len(candidates)} candidates!")
                        for idx, c in enumerate(candidates):
                            st.markdown(f"---\n### {idx+1}. {c['name']}")
                            st.write(c['headline'])
                            if c.get('full_headline') and c['full_headline'] != c['headline']:
                                with st.expander("🧠 Full Profile Snippet"):
                                    st.write(c['full_headline'])
                            url = c['linkedin_url']
                            if not url.startswith('http'):
                                url = 'https://' + url.lstrip('/')
                            st.markdown(f"[🔗 Open LinkedIn Profile]({url})", unsafe_allow_html=True)
                            if c.get('fit_score') is not None:
                                st.write(f"**Fit Score:** {float(c['fit_score']):.1f}")
                            if c.get('score_breakdown'):
                                st.write("**Rubric Breakdown:**")
                                for k, v in c['score_breakdown'].items():
                                    st.write(f"- {k.title()}: {float(v):.1f}")
                            if c.get('outreach_message'):
                                st.write("**Outreach Message:**")
                                st.code(c['outreach_message'])
                except Exception as e:
                    st.error(f"Error: {e}")

    if page == "AI Chat Assistant":
        st.header("💬 AI Chat Assistant")
        st.write("Ask any hiring, resume, or job search question and get an AI-powered answer!")
        st.info("For more personalized answers, upload a resume (PDF or TXT). The AI will use it as context for your questions.")
        uploaded = st.file_uploader("Upload a resume (optional)", type=["pdf", "txt"], key="chat_resume")
        if uploaded:
            import io
            if uploaded.type == "application/pdf":
                import PyPDF2
                reader = PyPDF2.PdfReader(uploaded)
                text = " ".join([page.extract_text() or '' for page in reader.pages])
            else:
                text = uploaded.read().decode("utf-8")
            parsed = extract_info(text)
            st.session_state['chat_resume_parsed'] = parsed
            st.success("Resume uploaded and parsed! The AI will use it for context.")
        resume_context = st.session_state.get('chat_resume_parsed', None)
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []
        user_input = st.text_input("Type your question:", key="chat_input")
        if st.button("Send") and user_input.strip():
            with st.spinner("Thinking..."):
                if resume_context:
                    answer = answer_question(user_input, resume_context)
                else:
                    answer = answer_question(user_input)
                st.session_state['chat_history'].append((user_input, answer))
        for q, a in reversed(st.session_state['chat_history']):
            st.markdown(f"**You:** {q}")
            st.markdown(f"**AI:** {a}") 