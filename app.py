from pyresparser import ResumeParser
import streamlit as st
import pandas as pd
import pdfplumber
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import plotly.express as px

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Initialize session state
for key in ["results", "analysis_done", "jd_text", "jd_keywords", "resume_files", "jd_file", "resume_files_input", "analyze_triggered"]:
    if key not in st.session_state:
        st.session_state[key] = [] if "files" in key or key == "jd_keywords" else False if "done" in key or "triggered" in key else ""

# 🔄 Reset button
if st.button("🔄 Reset App"):
    for key in ["results", "analysis_done", "jd_text", "jd_keywords", "resume_files", "analyze_triggered"]:
        st.session_state[key] = [] if "results" in key or key == "jd_keywords" else False if "done" in key or "triggered" in key else ""
    st.rerun()

# UI
st.title("📄 Resume Analyzer (HireAI)")

jd_file_input = st.file_uploader("Upload Job Description (TXT)", type=["txt"])
resume_files_input = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

# Store uploaded files in session state
if jd_file_input:
    st.session_state.jd_file = jd_file_input
if resume_files_input:
    st.session_state.resume_files_input = resume_files_input

# ✅ Always show Analyze button at top if files are uploaded
if st.session_state.jd_file and st.session_state.resume_files_input:
    st.markdown("### 🔍 Ready to Analyze Resumes")
    if st.button("🔍 Analyze Resumes"):
        st.session_state.analyze_triggered = True
        st.session_state.analysis_done = False

# Layout placeholders
progress_bar = st.empty()
status_text = st.empty()
chart_placeholder = st.empty()
rank_placeholder = st.empty()
resume_analysis_container = st.container()

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

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", text)
    return match.group(0) if match else "Not found"

def extract_experience(text):
    match = re.search(r"(\d+)\s+(?:years|yrs)\s+(?:of\s+)?experience", text, re.IGNORECASE)
    return f"{match.group(1)} years" if match else "Not found"

def calculate_semantic_similarity(text1, text2):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    similarity_score = util.pytorch_cos_sim(embedding1, embedding2)
    return float(similarity_score[0][0]) * 100

def extract_structured_experience(file_path):
    data = ResumeParser(file_path).get_extracted_data()
    print("🔍 Raw ResumeParser Output:", data)

    return {
        "Designation": data.get("designation", []),
        "Company Names": data.get("company_names", []),
        "Total Experience": data.get("total_experience", "Not found")
    }



# ✅ Run analysis only when triggered
if st.session_state.analyze_triggered and not st.session_state.analysis_done:
    st.session_state.jd_text = st.session_state.jd_file.read().decode("utf-8")
    st.session_state.jd_keywords = extract_keywords(st.session_state.jd_text)
    st.session_state.resume_files = st.session_state.resume_files_input
    st.session_state.results = []

    total_resumes = len(st.session_state.resume_files)
    progress_bar.progress(0)

    for idx, resume_file in enumerate(st.session_state.resume_files):
        status_text.text(f"🔍 Analyzing: {resume_file.name} ({idx}/{total_resumes})")

        resume_text = extract_text_from_pdf(resume_file)
        resume_keywords = extract_keywords(resume_text)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        experience = extract_experience(resume_text)
        structured_exp = extract_structured_experience(resume_file)
        documents = [st.session_state.jd_text, resume_text]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        jd_scores = tfidf_matrix[0].toarray()[0]
        resume_scores = tfidf_matrix[1].toarray()[0]

        tfidf_match_score = sum([jd_scores[i] for i in range(len(feature_names)) if jd_scores[i] > 0.1 and resume_scores[i] > 0]) / sum(jd_scores) * 100 if sum(jd_scores) > 0 else 0
        semantic_similarity_score = calculate_semantic_similarity(resume_text, st.session_state.jd_text)
        keyword_coverage_score = len(set(resume_keywords).intersection(set(st.session_state.jd_keywords))) / len(set(st.session_state.jd_keywords)) * 100 if st.session_state.jd_keywords else 0
        fit_score = (0.4 * tfidf_match_score) + (0.4 * semantic_similarity_score) + (0.2 * keyword_coverage_score)

        missing_keywords = [word for i, word in enumerate(feature_names) if jd_scores[i] > 0.1 and resume_scores[i] == 0]
        generic_terms = {"also", "us", "x", "join", "apply", "offer", "required", "preferred", "related", "within", "looking", "invite"}
        missing_keywords = [kw for kw in missing_keywords if kw not in generic_terms]

        result = {
            "Candidate": resume_file.name,
            "Email": email,
            "Contact": phone,
            "Experience": experience,
            "TF-IDF Match (%)": round(tfidf_match_score, 2),
            "Semantic Similarity (%)": round(semantic_similarity_score, 2),
            "Keyword Coverage (%)": round(keyword_coverage_score, 2),
            "Fit Score (%)": round(fit_score, 2),
            "Missing Keywords": ", ".join(missing_keywords),
            "Experience": structured_exp.get("Total Experience", "Not found"),
            "Experience Details": structured_exp
        }

        st.session_state.results.append(result)

        df_so_far = pd.DataFrame(st.session_state.results).sort_values(by="Fit Score (%)", ascending=False).reset_index(drop=True)
        df_so_far.index += 1
        df_so_far.index.name = "Rank"

        with chart_placeholder.container():
            st.subheader("📊 Fit Score Comparison")
            fig = px.bar(df_so_far, x="Candidate", y="Fit Score (%)", color="Candidate", title="Fit Score per Candidate")
            st.plotly_chart(fig, key=f"realtime_chart_{idx}")

        with rank_placeholder.container():
            st.subheader("🏆 Ranked Candidates by Fit Score")
            st.dataframe(df_so_far)

        progress_bar.progress((idx + 1) / total_resumes)

    status_text.text("✅ All resumes analyzed successfully!")
    st.session_state.analysis_done = True

# ✅ Re-render everything if analysis is done
if st.session_state.analysis_done and st.session_state.results:
    df_final = pd.DataFrame(st.session_state.results).sort_values(by="Fit Score (%)", ascending=False).reset_index(drop=True)
    df_final.index += 1
    df_final.index.name = "Rank"

    with chart_placeholder.container():
        st.subheader("📊 Fit Score Comparison")
        fig = px.bar(df_final, x="Candidate", y="Fit Score (%)", color="Candidate", title="Fit Score per Candidate")
        st.plotly_chart(fig, key="final_chart")

    with rank_placeholder.container():
        st.subheader("🏆 Ranked Candidates by Fit Score")
        st.dataframe(df_final)

        csv = df_final.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download All Results as CSV",
            data=csv,
            file_name="resume_analysis_results.csv",
            mime="text/csv",
            key="download_rank_table"
        )

    with resume_analysis_container.container():
        for result in st.session_state.results:
            st.subheader(f"📄 Analysis for {result['Candidate']}")
            st.metric("Fit Score (%)", result["Fit Score (%)"])

            with st.expander("📋 Detailed Analysis"):
                st.write(f"**Email Address:** {result['Email']}")
                st.write(f"**Contact Number:** {result['Contact']}")
                designations = result['Experience Details'].get('Designation', [])
                companies = result['Experience Details'].get('Company Names', [])

                st.write("**Total Experience:**", result['Experience Details'].get('Total Experience', 'Not found'))
                st.write("**Designations:**", ", ".join(designations) if isinstance(designations, list) else designations)
                st.write("**Companies:**", ", ".join(companies) if isinstance(companies, list) else companies)

                st.write(f"**Fit Score (%):** {result["Fit Score (%)"]}")
                st.write(f"**TF-IDF Match Score:** {result['TF-IDF Match (%)']}%")
                st.write(f"**Semantic Similarity Score:** {result['Semantic Similarity (%)']}%")
                st.write(f"**Keyword Coverage Score:** {result['Keyword Coverage (%)']}%")
                st.write("**Missing Keywords:**")
                st.write(result['Missing Keywords'] if result['Missing Keywords'] else "None ✅")
