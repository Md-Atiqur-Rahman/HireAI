import streamlit as st
import pandas as pd
import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util
import plotly.express as px

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
st.title("📄 Resume Analyzer")

jd_file = st.file_uploader("Upload Job Description (TXT)", type=["txt"])
resume_files = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

if jd_file and resume_files:
    if st.button("🔍 Analyze Resumes"):
        jd_text = jd_file.read().decode("utf-8")
        jd_keywords = extract_keywords(jd_text)

        results = []
        for resume_file in resume_files:
            resume_text = extract_text_from_pdf(resume_file)
            resume_keywords = extract_keywords(resume_text)

            matched_keywords = resume_keywords.intersection(jd_keywords)
            missing_keywords = jd_keywords.difference(resume_keywords)
            match_score = len(matched_keywords) / len(jd_keywords) * 100 if jd_keywords else 0
            similarity_score = calculate_similarity(resume_text, jd_text)
            fit_score = (0.6 * match_score) + (0.4 * similarity_score)

            results.append({
                "Candidate": resume_file.name,
                "Match Score (%)": round(match_score, 2),
                "Similarity Score (%)": round(similarity_score, 2),
                "Fit Score (%)": round(fit_score, 2),
                "Missing Keywords": ", ".join(missing_keywords)
            })

        df = pd.DataFrame(results)

        st.subheader("📊 Fit Score Comparison")
        fig = px.bar(df, x="Candidate", y="Fit Score (%)", color="Candidate", title="Fit Score per Candidate")
        st.plotly_chart(fig)

        st.subheader("📋 Detailed Analysis")
        for result in results:
            with st.expander(f"Candidate: {result['Candidate']}"):
                st.write(f"**Match Score:** {result['Match Score (%)']}%")
                st.write(f"**Similarity Score:** {result['Similarity Score (%)']}%")
                st.write(f"**Fit Score:** {result['Fit Score (%)']}%")
                st.write("**Missing Keywords:**")
                st.write(result['Missing Keywords'] if result['Missing Keywords'] else "None ✅")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Results as CSV", data=csv, file_name="resume_analysis_results.csv", mime="text/csv")
