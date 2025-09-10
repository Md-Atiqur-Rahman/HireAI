import os
from src.parser import extract_text_from_pdf
from src.extractor import extract_keywords
from src.scorer import calculate_similarity

# Load job description
with open("E:/Thesis/resume-analyzer/job_descriptions/software_engineer.txt", "r", encoding="utf-8") as f:
    jd_text = f.read()
jd_keywords = extract_keywords(jd_text)

# Folder containing resumes
resume_folder = "resumes"

# Loop through all PDF files
for filename in os.listdir(resume_folder):
    if filename.endswith(".pdf"):
        resume_path = os.path.join(resume_folder, filename)
        resume_text = extract_text_from_pdf(resume_path)
        resume_keywords = extract_keywords(resume_text)

        # Keyword matching
        matched_keywords = resume_keywords.intersection(jd_keywords)
        missing_keywords = jd_keywords.difference(resume_keywords)
        match_score = len(matched_keywords) / len(jd_keywords) * 100 if jd_keywords else 0

        # Semantic similarity
        similarity_score = calculate_similarity(resume_text, jd_text)

        # Fit score
        fit_score = (0.6 * match_score) + (0.4 * similarity_score)

        # Print results
        print(f"\n📄 Resume: {filename}")
        print(f"✅ Keyword Match Score: {match_score:.2f}%")
        print(f"🔍 Semantic Similarity Score: {similarity_score:.2f}%")
        print(f"🏆 Fit Score: {fit_score:.2f}%")
        print(f"❌ Missing Keywords: {missing_keywords}")
