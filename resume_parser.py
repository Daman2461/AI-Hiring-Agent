import spacy
import re
from typing import Dict

nlp = spacy.load('en_core_web_sm')

EMAIL_REGEX = r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+"
PHONE_REGEX = r"\b\d{10}\b|\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}"  # US phone patterns

SKILLS = [
    'python', 'java', 'c++', 'machine learning', 'deep learning', 'nlp', 'data analysis',
    'project management', 'sql', 'aws', 'azure', 'docker', 'kubernetes', 'react', 'node.js'
]

def extract_info(text: str) -> Dict:
    doc = nlp(text)
    name = None
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name = ent.text
            break
    email = re.findall(EMAIL_REGEX, text)
    phone = re.findall(PHONE_REGEX, text)
    skills_found = [skill for skill in SKILLS if skill.lower() in text.lower()]
    return {
        'name': name,
        'email': email[0] if email else None,
        'phone': phone[0] if phone else None,
        'skills': skills_found
    } 