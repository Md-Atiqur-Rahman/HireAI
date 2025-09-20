import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", text)
    return match.group(0) if match else "Not found"

def extract_date_ranges(text):
    # Use regex to find date ranges
    pattern = r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}|\\d{2}/\\d{4})\\s*(?:–|-|to)\\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s\\d{4}|\\d{2}/\\d{4})"
    return re.findall(pattern, text)

def extract_keywords(text):
    tokens = word_tokenize(text.lower())
    return [word for word in tokens if word.isalpha() and word not in stopwords.words('english')]

def extract_entities(text):
    doc = nlp(text)
    name = ""
    organizations = set()
    designations = set()

    for ent in doc.ents:
        if ent.label_ == "PERSON" and not name:
            # Clean up the name
            raw_name = ent.text.strip()
            cleaned_name = re.split(r"[\n:]", raw_name)[0].strip()
            cleaned_name = re.sub(r"\bEmail\b", "", cleaned_name, flags=re.IGNORECASE).strip()
            name = cleaned_name
        elif ent.label_ == "ORG":
            organizations.add(ent.text)

    designation_matches = re.findall(r"\b(Developer|Engineer|Manager|Intern|Analyst|Consultant|Creator)\b", text, re.IGNORECASE)
    designations.update(designation_matches)

    return {
        "Name": name,
        "Organizations": list(organizations),
        "Designations": list(designations)
    }

def filter_organizations(orgs, text):
    filtered = []
    for org in orgs:
        if re.search(rf"\b{re.escape(org)}\b", text, re.IGNORECASE):
            # Check if org appears near keywords like 'worked at', 'interned at', etc.
            context = re.search(rf".{{0,50}}{re.escape(org)}.{{0,50}}", text, re.IGNORECASE)
            if context and any(kw in context.group().lower() for kw in ["intern", "worked", "developer", "engineer", "creator"]):
                filtered.append(org)
    return filtered

def clean_list(items):
    return list(set([item.strip().title() for item in items if len(item) > 2]))


# 🔹Designations & Organizations
def clean_list(items):
    return list(set([item.strip().title() for item in items if len(item) > 2]))


import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

import re

import re

import re

import re

def extract_name_from_text(resume_text, email=None):
    """
    Extract candidate's name from resume text.
    """
    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]

    # First, check for explicit 'Name:' pattern
    for line in lines[:15]:
        match = re.match(r"(?i)^name[:\-]\s*(.+)$", line)  # case-insensitive
        if match:
            name_candidate = match.group(1).strip()
            # remove extra symbols
            name_candidate = re.sub(r"[^A-Za-z\s\.\-]", "", name_candidate)
            if name_candidate:
                return name_candidate

    # Fallback: scan top lines for probable name
    for line in lines[:15]:
        # Remove unwanted patterns like (cid:xxx) or numbers
        cleaned_line = re.sub(r"\(cid:\d+\)|[0-9\+\-]", "", line).strip()

        # Skip lines with keywords
        lower_line = cleaned_line.lower()
        if any(keyword in lower_line for keyword in ["contact", "phone", "email", "github", "linkedin", "address", "skills", "experience", "roll no", "youtube"]):
            continue

        # If line has mostly letters and spaces, consider it a name
        if re.match(r"^[A-Za-z\s\.]+$", cleaned_line) and 1 <= len(cleaned_line.split()) <= 5:
            return cleaned_line

    # Fallback: get name from email
    if email:
        username = email.split("@")[0]
        name_parts = username.replace(".", " ").replace("_", " ").title()
        return name_parts

    return "Unknown"


