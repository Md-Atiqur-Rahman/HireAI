import ast
from datetime import datetime
import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.Helper.banner_style import banner_style
from src.Helper.extract_skills import extract_skills_tfidf
from src.Helper.extract_general_info import extract_email, extract_name_from_text, extract_phone
from src.database.db_candidates import save_candidate
from src.database.db_job_category import get_all_categories
from src.database.db_job_requirements import get_requirements_by_category
from src.feature.helper_requirement_analyzer.requirement_analysis import evaluate_resume
from src.Helper.parser import extract_text_from_pdf

# ============================
# Resume Analysis Page
# ============================


# Load categories and requirements




def resume_uploader():
    # st.title("Resume Analyzer (HireAI)")
    banner_style("Resume Analyzer 🔍")
    # categories = get_categories()
    # selected_category = st.selectbox("Select Job Requirement Category", ["All"] + categories)
    categories = get_all_categories()  # [(id, name), ...]
    job_requirements = []
    if not categories:
        st.warning("No categories found. Please add a category first.")
    else:
        category_dict = {cat['name']: cat['id'] for cat in categories} 

    # Dropdown shows only names
        selected_category_name = st.selectbox("Select Job Category", list(category_dict.keys()))

    # Get corresponding ID
        selected_category_id = category_dict[selected_category_name]
        job_requirements = get_requirements_by_category(selected_category_id)

    if not job_requirements:
        st.warning("No job requirements found for this category.")

    uploaded_file = st.file_uploader("Upload Candidate Resume (PDF or TXT)", type=["pdf", "txt"])

    if uploaded_file and job_requirements:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = str(uploaded_file.read(), "utf-8")
        
        #print("job_requirements:",job_requirements)
        #job_requirements = "{'Experience': ['Full Stack Developer with 3 years of experience in C#, .Net'], 'Education': ['Bachelor’s degree in Computer Science'], 'TechnicalSkills': ['Strong in ASP.NET Core, MVC, Web API, MS SQL.', 'Experience with Angular or React for front-end development.', 'Familiarity with cloud platforms (Azure/AWS) and Git version control.'], 'Others': ['Project Management skills on Agile scrum', 'Fluent in oral and written communication in English']}"

        #job_requirements_str = "{'Experience': ['Full Stack Developer with 3 years of experience in C#, .Net'], 'Education': ['Bachelor’s degree in Computer Science'], 'TechnicalSkills': ['Strong in ASP.NET Core, MVC, Web API, MS SQL.', 'Experience with Angular or React for front-end development.', 'Familiarity with cloud platforms (Azure/AWS) and Git version control.'], 'Others': ['Project Management skills on Agile scrum', 'Fluent in oral and written communication in English']}"  

        # convert string → dict
        #job_requirements = ast.literal_eval(job_requirements_str)

        summary_text, total_exp, total_score,technicalskills = evaluate_resume(resume_text, job_requirements)
        print("resume_text:------------\n",resume_text)
        print("job_requirements:--------------\n",job_requirements)
        print("skills:-------------\n",technicalskills)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)
        name = extract_name_from_text(resume_text,email)
        #skills = extract_skills_tfidf(resume_text,"\n".join(job_requirements))
        save_candidate(name, email, phone, total_exp, total_score,technicalskills , summary_text, selected_category_id)
        # summary_text = summarize_results(results)
        st.subheader("Resume Evaluation Summary")
        st.text(summary_text) 
        


