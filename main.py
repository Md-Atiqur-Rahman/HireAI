import re
from dateutil import parser
from datetime import datetime
import spacy
from sentence_transformers import SentenceTransformer, util

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
        required_years = int(re.search(r"(\d+)", requirement).group(1))

        # Step 1: Try advanced extraction
        _, total_years = extract_experience_entries(resume_text)

        # Step 2: Try regex fallback if advanced extraction fails
        if total_years == 0:
            total_years = extract_years_from_text(resume_text)

        # Step 3: Determine status
        status = "✅ Match" if total_years >= required_years else "❌ Missing"
        experience_check = f"Requirement: {required_years}+ years, Candidate: {total_years} years"

        # Continue with SBERT + keyword analysis for skills part
        req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
        res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
        sims = util.cos_sim(req_emb, res_embs)[0]
        best_idx = int(sims.argmax())
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

    # Generic SBERT similarity check
    req_emb = sbert_model.encode(requirement, convert_to_tensor=True)
    res_embs = sbert_model.encode(resume_sentences, convert_to_tensor=True)
    sims = util.cos_sim(req_emb, res_embs)[0]
    best_idx = int(sims.argmax())
    best_score = float(sims[best_idx])
    best_sentence = resume_sentences[best_idx] if resume_sentences else ""
    req_keywords = extract_keywords(requirement)
    matched = req_keywords & resume_keywords
    missing = req_keywords - resume_keywords

    return {
        "requirement": requirement,
        "status": "✅ Match" if best_score >= 0.70 else "❌ Missing",
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



# Job Requirements
job_requirements = [
    "5+ years of development experience in SQL / C# / Python",
    "Developed and executed medium to large-scale features",
    "Implement automation tools and frameworks (CI/CD pipelines)",
    "Bachelor’s or master’s degree in Computer Science or Engineering",
    "Experience with BigQuery, dbt, Snowflake",
    "Experience in data visualization/Looker/NetSpring",
    "Understanding the value of pair programming/TDD/Clean Code",
    "Exposure/Experience leveraging AI"
]

# Candidate Resume
candidate_resume = """
Software Engineer with 5 years of experience in C# and SQL.
Worked on feature development and bug fixing for enterprise projects.
Familiar with GitHub Actions for CI/CD pipelines.
Holds a Bachelor's degree in Computer Science.
Worked with MongoDB and Oracle databases.
No experience with BigQuery, dbt, or Snowflake.
No knowledge of Looker/NetSpring tools.
Practices clean code principles and pair programming occasionally.
Learning AI concepts but no production experience yet.
"""
# Extract Resume from PDF
resume_text = extract_text_from_pdf( "E:/Thesis/resume-analyzer/resumes/Md Atiqur Rahman.pdf")

summary, results = evaluate_resume(candidate_resume, job_requirements)

print(summary)
for r in results:
    print(f"\n{r['requirement']}")
    print(f"   ➤ Status: {r['status']} (score={r.get('score', 0.5)})")
    if 'experience_check' in r:
        print(f"   ➤ Experience Check: {r['experience_check']}")
    print(f"   ➤ Best Resume Match: {r['best_sentence']}")
    print(f"   ➤ Matched Keywords: {', '.join(r['matched_keywords']) if r['matched_keywords'] else 'None'}")
    print(f"   ➤ Missing Keywords: {', '.join(r['missing_keywords']) if r['missing_keywords'] else 'None'}")

