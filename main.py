import os
import pandas as pd
from tabulate import tabulate
import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Helper functions
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_keywords(text):
    tokens = word_tokenize(text.lower())
    keywords = [word for word in tokens if word.isalpha() and word not in stopwords.words('english')]
    return set(keywords)

def calculate_similarity(text1, text2):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(embedding1, embedding2)
    return float(similarity_score[0][0]) * 100

# Load job description
with open("job_descriptions/software_engineer.txt", "r", encoding="utf-8") as f:
    jd_text = f.read()
jd_keywords = extract_keywords(jd_text)

# Analyze resumes
results = []
resume_folder = "resumes"
for filename in os.listdir(resume_folder):
    if filename.endswith(".pdf"):
        resume_path = os.path.join(resume_folder, filename)
        resume_text = extract_text_from_pdf(resume_path)
        resume_keywords = extract_keywords(resume_text)

        matched_keywords = resume_keywords.intersection(jd_keywords)
        missing_keywords = jd_keywords.difference(resume_keywords)
        match_score = len(matched_keywords) / len(jd_keywords) * 100 if jd_keywords else 0
        similarity_score = calculate_similarity(resume_text, jd_text)
        fit_score = (0.6 * match_score) + (0.4 * similarity_score)

        results.append({
            "Candidate": filename,
            "Match Score (%)": round(match_score, 2),
            "Similarity Score (%)": round(similarity_score, 2),
            "Fit Score (%)": round(fit_score, 2),
            "Missing Keywords": ", ".join(missing_keywords)
        })

# Display table
df = pd.DataFrame(results)
print(tabulate(df, headers='keys', tablefmt='grid'))

# Export to CSV
df.to_csv("resume_analysis_results.csv", index=False)
print("\n✅ Results exported to resume_analysis_results.csv")
