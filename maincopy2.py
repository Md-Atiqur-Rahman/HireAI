import re
import spacy
from sentence_transformers import SentenceTransformer, util
import torch

import pdfplumber
import spacy
from sentence_transformers import SentenceTransformer, util
import torch

from src.Helper.extract_experience_details import extract_experience_entries, extract_years_from_text

# Load models
nlp = spacy.load("en_core_web_sm")
sbert = SentenceTransformer("all-MiniLM-L6-v2")

# --- PDF Reader ---
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

# --- Keyword Extractor ---
def extract_keywords(text):
    doc = nlp(text)
    return {token.lemma_.lower() for token in doc 
            if token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"] and not token.is_stop}

# --- Requirement Checker ---
def check_requirement(requirement, resume_sentences, resume_keywords,total_years, threshold=0.6):
    req_embedding = sbert.encode(requirement, convert_to_tensor=True)
    resume_embeddings = sbert.encode(resume_sentences, convert_to_tensor=True)
    similarities = util.cos_sim(req_embedding, resume_embeddings)[0]

    best_idx = int(torch.argmax(similarities))
    best_score = float(similarities[best_idx])
    best_match = resume_sentences[best_idx] if resume_sentences else ""

    req_keywords = extract_keywords(requirement)
    matched_keywords = req_keywords.intersection(resume_keywords)
    missing_keywords = req_keywords - matched_keywords

    # --- Years of Experience Logic ---
    status = "❌ Missing"
    exp_match = None
    year_pattern = re.search(r"(\d+)\+?\s*years?", requirement.lower())
    if year_pattern:
        required_years = int(year_pattern.group(1))
        if total_years == 0:
            total_years = extract_years_from_text(resume_text)
            print("total_years------------",total_years)
        if total_years >= required_years:
            status = "✅ Match"
            exp_match = f"Requirement: {required_years}+ years, Candidate: {total_years} years"
        else:
            status = "❌ Missing"
            exp_match = f"Requirement: {required_years}+ years, Candidate: {total_years} years"
    else:
        # Fall back to SBERT similarity threshold
        status = "✅ Match" if best_score >= threshold else "❌ Missing"
    return {
        "requirement": requirement,
        "best_match_sentence": best_match,
        "similarity_score": round(best_score, 2),
        "status": status,
        "experience_check": exp_match,
        "matched_keywords": list(matched_keywords),
        "missing_keywords": list(missing_keywords)
    }

# --- MAIN EXECUTION ---

# Job Requirements
job_requirements = [
    # "5+ years of development experience in SQL / C# / Python",
    # "Developed and executed medium to large-scale features",
    "Implement automation tools and frameworks (CI/CD pipelines)",
    # "Bachelor’s or master’s degree in Computer Science or Engineering",
    # "Experience with BigQuery, dbt, Snowflake",
    # "Experience in data visualization/Looker/NetSpring",
    # "Understanding the value of pair programming/TDD/Clean Code",
    # "Exposure/Experience leveraging AI"
]

# Candidate Resume
resume_text = """
Software Engineer with 3 years of experience in C# and SQL.
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
# resume_text = extract_text_from_pdf( "E:/Thesis/resume-analyzer/resumes/Md Atiqur Rahman.pdf")




experience_entries, total_years = extract_experience_entries(resume_text)
total_years = extract_years_from_text(resume_text)

# Split resume into sentences
resume_sentences = [s.strip() for s in resume_text.split("\n") if s.strip()]

# Extract keywords from resume
resume_keywords = extract_keywords(resume_text)

# Run analysis
results = [check_requirement(req, resume_sentences, resume_keywords, total_years) 
           for req in job_requirements]

# --- Summary Report ---
total = len(results)
matched = sum(1 for r in results if r["status"] == "✅ Match")
missing = total - matched

print("📊 SUMMARY REPORT")
print(f"Your profile matches {matched} of the {total} required qualifications.")
print(f"✅ Matched: {matched}")
print(f"❌ Missing: {missing}")
print("-" * 60)

# --- Detailed Breakdown ---
for r in results:
    print(f"{r['requirement']}")
    print(f"   ➤ Status: {r['status']} (score={r['similarity_score']})")
    if r["experience_check"]:
        print(f"   ➤ Experience Check: {r['experience_check']}")
    print(f"   ➤ Best Resume Match: {r['best_match_sentence']}")
    print(f"   ➤ Matched Keywords: {', '.join(r['matched_keywords']) if r['matched_keywords'] else 'None'}")
    print(f"   ➤ Missing Keywords: {', '.join(r['missing_keywords']) if r['missing_keywords'] else 'None'}")
    print()