import re
from dateutil import parser
from datetime import datetime
import spacy
from sentence_transformers import SentenceTransformer, util
import torch

from src.Helper.parser import extract_text_from_pdf

# ===============================
# Load Models
# ===============================
nlp = spacy.load("en_core_web_sm")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# ===============================
# Experience Extractor
# ===============================
def extract_experience_entries(text):
    experience_entries = []
    total_months = 0

    patterns = [
        r"(?P<title>.*?)\n(?P<company>.*?)\n\[(?P<start>\d{2}/\d{4})\]\s*-\s*(\[(?P<end>\d{2}/\d{4})\]|(?P<present>Present))",
        r"(?P<title>.*?)\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*(\[(?P<end>\d{2}/\d{4})\]|(?P<present>Present))\s*(?P<company>[A-Za-z0-9 ,.&()]+)",
        r"(?P<title>.*?)\s*:\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*\[(?P<end>\d{2}/\d{4}|Present)\]",
        r"(?P<title>.*?)\s+at\s+(?P<company>.*?)\s*\[(?P<start>\d{2}/\d{4})\]\s*-\s*\[(?P<end>\d{2}/\d{4}|Present)\]",
        r"(?P<title>.*?)\n(?P<company>.*?)\n(?P<start>\d{2}/\d{4})\s*-\s*(?P<end>\d{2}/\d{4}|Present)",
        r"(?P<title>.+?),\s*(?P<company>.+?)\n(?P<start>[A-Za-z\.]+ \d{4})\s*-\s*(?P<end>[A-Za-z\.]+ \d{4}|Present)",
    ]

    matches = []
    for pat in patterns:
        matches += list(re.finditer(pat, text))

    for match in matches:
        title = match.group("title").strip()
        company = match.group("company").strip() if "company" in match.groupdict() and match.group("company") else ""
        start = match.group("start")
        end = match.group("end") if match.group("end") else match.group("present")

        try:
            start_date = parser.parse(start)
            end_date = datetime.now() if end.lower() == "present" else parser.parse(end)
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            total_months += months
            years_fraction = round(months / 12, 1)
            formatted = f"{title} - {company}: [{start}] - [{end}] = {months} months ({years_fraction} years)"
            experience_entries.append(formatted)
        except:
            continue

    total_years = round(total_months / 12, 1)
    return experience_entries, total_years

def extract_years_from_text(text):
    patterns = [
        r"(\d+)\+?\s+years of experience",
        r"over (\d+)\s+years",
        r"more than (\d+)\s+years"
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0

# ===============================
# Keyword Extractor
# ===============================
def extract_keywords(text):
    doc = nlp(text.lower())
    return {token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN", "VERB"]}

# ===============================
# Requirement Checker
# ===============================
def check_requirement(requirement, resume_sentences, resume_keywords, resume_text):
    # Handle experience requirement separately
    if "year" in requirement.lower():
        # Detect range "X-Y years"
        range_match = re.search(r"(\d+)\s*-\s*(\d+)\s*years", requirement, re.IGNORECASE)
        single_match = re.search(r"(\d+)\+?\s*years", requirement, re.IGNORECASE)

        min_years, max_years = None, None
        if range_match:
            min_years, max_years = int(range_match.group(1)), int(range_match.group(2))
        elif single_match:
            min_years = int(single_match.group(1))

        # Step 1: Try advanced extraction
        _, total_years = extract_experience_entries(resume_text)

        # Step 2: Fallback regex if advanced extraction fails
        if total_years == 0:
            total_years = extract_years_from_text(resume_text)

        # Step 3: Check requirement match
        if min_years is not None and max_years is not None:  
            status = "✅ Match" if min_years <= total_years <= max_years else "❌ Missing"
            experience_check = f"Requirement: {min_years}-{max_years} years, Candidate: {total_years} years"
        elif min_years is not None:  
            status = "✅ Match" if total_years >= min_years else "❌ Missing"
            experience_check = f"Requirement: {min_years}+ years, Candidate: {total_years} years"
        else:
            status = "❌ Missing"
            experience_check = f"Requirement unclear, Candidate: {total_years} years"

        # Continue with SBERT + keyword analysis for skills part
        req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
        res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
        sims = util.cos_sim(req_emb, res_embs)[0]
        best_idx = int(torch.argmax(sims))
        best_score = float(sims[best_idx])
        best_sentence = resume_sentences[best_idx] if resume_sentences else ""
        req_keywords = extract_keywords(requirement)
        matched = req_keywords & resume_keywords
        missing = req_keywords - resume_keywords

        return {
            "requirement": requirement,
            "status": status,
            "score": round(best_score, 2),
            "experience_check": experience_check,
            "best_sentence": best_sentence,
            "matched_keywords": list(matched),
            "missing_keywords": list(missing)
        }

    # ==========================
    # Generic (non-experience) requirement check
    # ==========================
    req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
    res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
    sims = util.cos_sim(req_emb, res_embs)[0]
    best_idx = int(torch.argmax(sims))
    best_score = float(sims[best_idx])
    best_sentence = resume_sentences[best_idx] if resume_sentences else ""
    req_keywords = extract_keywords(requirement)
    matched = req_keywords & resume_keywords
    missing = req_keywords - resume_keywords

    return {
        "requirement": requirement,
        "status": "✅ Match" if best_score >= 0.5 else "❌ Missing",
        "score": round(best_score, 2),
        "best_sentence": best_sentence,
        "matched_keywords": list(matched),
        "missing_keywords": list(missing)
    }

# ===============================
# Runner
# ===============================
def evaluate_resume(resume_text, job_requirements):
    resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]
    resume_keywords = extract_keywords(resume_text)

    results = [check_requirement(req, resume_sentences, resume_keywords, resume_text) for req in job_requirements]

    # Summary like LinkedIn
    met_count = sum(1 for r in results if r["status"].startswith("✅"))
    total_count = len(results)
    summary = f"Matches {met_count} of the {total_count} required qualifications"

    return summary, results

def summarize_results(results):
    # Assign weights (higher for experience & education, lower for skills)
    weights = {
        "experience": 3,
        "education": 2,
        "skills": 1
    }

    total_weight = 0
    earned_weight = 0

    matched = []
    missing = []

    for r in results:
        req = r["requirement"].lower()
        status = r["status"]

        # Figure out category
        if "year" in req or "experience" in req:
            category = "experience"
        elif "degree" in req or "bachelor" in req or "master" in req:
            category = "education"
        else:
            category = "skills"

        weight = weights[category]
        total_weight += weight

        if status.startswith("✅"):
            earned_weight += weight
            matched.append(r["requirement"])
        else:
            missing.append(r["requirement"])

    overall_score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0

    # Build LinkedIn-style summary with actual newlines
    lines = [
        "📊 Summary:",
        f"\n✅ Matches {len(matched)} of {len(results)} required qualifications",
        f"\n📌 Matches Requirements:\n   ✅ " + "\n   ✅ ".join(matched) if matched else "📌 Strong in: None",
        f"\n⚠️ Missing Requirements:\n   ❌ " + "\n   ❌ ".join(missing) if missing else "⚠️ Missing: None",
        f"\n🔢 Score: {overall_score}%"
    ]

    return "\n".join(lines)
