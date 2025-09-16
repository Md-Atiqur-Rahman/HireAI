import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.db_job_requirements import get_categories, get_requirements_by_category
from src.feature.resume_analyzer.requirement_analysis import evaluate_resume, summarize_results
from src.Helper.parser import extract_text_from_pdf

# ============================
# Resume Analysis Page
# ============================
st.title("Resume Analyzer")

# Load categories and requirements




def resume_uploader():

    categories = get_categories()
    selected_category = st.selectbox("Select Job Requirement Category", ["All"] + categories)
    job_requirements = get_requirements_by_category(selected_category)

    if not job_requirements:
        st.warning("No job requirements found for this category.")

    uploaded_file = st.file_uploader("Upload Candidate Resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file and job_requirements:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = str(uploaded_file.read(), "utf-8")

        summary, results = evaluate_resume(resume_text, job_requirements)
        summary_text = summarize_results(results)
        st.subheader("Resume Evaluation Summary")
        st.text(summary_text) 
        


