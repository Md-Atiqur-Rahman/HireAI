from src.parser import extract_text_from_pdf
from src.extractor import extract_keywords

# Load resume
resume_path = "E:/Thesis/resume-analyzer/resumes/Md Atiqur Rahman.pdf"
resume_text = extract_text_from_pdf(resume_path)
resume_keywords = extract_keywords(resume_text)

# Load job description
with open("E:/Thesis/resume-analyzer/job_descriptions/software_engineer.txt", "r", encoding="utf-8") as f:
    jd_text = f.read()
jd_keywords = extract_keywords(jd_text)

# Compare keywords
matched_keywords = resume_keywords.intersection(jd_keywords)
missing_keywords = jd_keywords.difference(resume_keywords)

# Calculate scores
match_score = len(matched_keywords) / len(jd_keywords) * 100 if jd_keywords else 0

# Print results
print("✅ Matched Keywords:", matched_keywords)
print("❌ Missing Keywords:", missing_keywords)
print(f"📊 Keyword Match Score: {match_score:.2f}%")
