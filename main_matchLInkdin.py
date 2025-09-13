import spacy
from sentence_transformers import SentenceTransformer, util
import torch

# Load models
nlp = spacy.load("en_core_web_sm")
sbert = SentenceTransformer("all-MiniLM-L6-v2")

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

import pdfplumber

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


# --- Helper Functions ---
def extract_keywords(text):
    """Extract keywords (nouns, verbs, adjectives) using spaCy"""
    doc = nlp(text)
    return {token.lemma_.lower() for token in doc 
            if token.pos_ in ["NOUN", "PROPN", "VERB", "ADJ"] and not token.is_stop}

def check_requirement(requirement, resume_sentences, resume_keywords, threshold=0.6):
    # SBERT similarity
    req_embedding = sbert.encode(requirement, convert_to_tensor=True)
    resume_embeddings = sbert.encode(resume_sentences, convert_to_tensor=True)
    similarities = util.cos_sim(req_embedding, resume_embeddings)[0]

    best_idx = int(torch.argmax(similarities))
    best_score = float(similarities[best_idx])
    best_match = resume_sentences[best_idx]

    # Keyword analysis
    req_keywords = extract_keywords(requirement)
    matched_keywords = req_keywords.intersection(resume_keywords)
    missing_keywords = req_keywords - matched_keywords

    return {
        "requirement": requirement,
        "best_match_sentence": best_match,
        "similarity_score": round(best_score, 2),
        "status": "✅ Match" if best_score >= threshold else "❌ Missing",
        "matched_keywords": list(matched_keywords),
        "missing_keywords": list(missing_keywords)
    }

# --- Main Logic ---
# candidate_resume = extract_text_from_pdf( "E:/Thesis/resume-analyzer/resumes/Md Atiqur Rahman.pdf")
resume_sentences = [s.strip() for s in candidate_resume.split("\n") if s.strip()]
resume_keywords = extract_keywords(candidate_resume)

results = [check_requirement(req, resume_sentences, resume_keywords) for req in job_requirements]

# --- Print Results ---
for r in results:
    print(f"{r['requirement']}")
    print(f"   ➤ Status: {r['status']} (score={r['similarity_score']})")
    print(f"   ➤ Best Resume Match: {r['best_match_sentence']}")
    print(f"   ➤ Matched Keywords: {', '.join(r['matched_keywords']) if r['matched_keywords'] else 'None'}")
    print(f"   ➤ Missing Keywords: {', '.join(r['missing_keywords']) if r['missing_keywords'] else 'None'}")
    print()
