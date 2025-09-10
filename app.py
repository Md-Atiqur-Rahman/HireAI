import streamlit as st
import pandas as pd
import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
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
    return [word for word in tokens if word.isalpha() and word not in stopwords.words('english')]

# Streamlit UI
st.title("📄 Resume Analyzer with TF-IDF Keyword Prioritization")

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

            # TF-IDF relevance scoring
            documents = [jd_text, resume_text]
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()
            jd_scores = tfidf_matrix[0].toarray()[0]
            resume_scores = tfidf_matrix[1].toarray()[0]

            missing_keywords = []
            for i, word in enumerate(feature_names):
                if jd_scores[i] > 0.1 and resume_scores[i] == 0:
                    missing_keywords.append(word)

            # Optional: filter out generic terms
            generic_terms = {
                "also", "us", "x", "join", "apply", "offer", "required", "preferred",
                "related", "within", "looking", "invite"
            }
            missing_keywords = [kw for kw in missing_keywords if kw not in generic_terms]

            match_score = len(set(resume_keywords).intersection(set(jd_keywords))) / len(set(jd_keywords)) * 100 if jd_keywords else 0
            fit_score = match_score  # simplified fit score using match only

            results.append({
                "Candidate": resume_file.name,
                "Match Score (%)": round(match_score, 2),
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
                st.write(f"**Fit Score:** {result['Fit Score (%)']}%")
                st.write("**Missing Keywords:**")
                st.write(result['Missing Keywords'] if result['Missing Keywords'] else "None ✅")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Results as CSV", data=csv, file_name="resume_analysis_results.csv", mime="text/csv")
