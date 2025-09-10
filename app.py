import streamlit as st
import pandas as pd
import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Helper functions
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
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

# Streamlit UI
st.title("📄 Simple Resume Analyzer")

# Upload resume
resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

# Input job description
jd_text = st.text_area("Paste Job Description Here")

# Analyze button
if resume_file and jd_text:
    if st.button("🔍 Analyze Resume"):
        resume_text = extract_text_from_pdf(resume_file)
        jd_keywords = extract_keywords(jd_text)
        resume_keywords = extract_keywords(resume_text)

        matched_keywords = resume_keywords.intersection(jd_keywords)
        missing_keywords = jd_keywords.difference(resume_keywords)
        match_score = len(matched_keywords) / len(jd_keywords) * 100 if jd_keywords else 0
        similarity_score = calculate_similarity(resume_text, jd_text)
        fit_score = (0.6 * match_score) + (0.4 * similarity_score)

        # Display results
        st.subheader("📊 Analysis Results")
        st.write(f"**Match Score:** {round(match_score, 2)}%")
        st.write(f"**Similarity Score:** {round(similarity_score, 2)}%")
        st.write(f"**Fit Score:** {round(fit_score, 2)}%")
        st.write("**Missing Keywords:**")
        st.write(", ".join(missing_keywords) if missing_keywords else "None ✅")
