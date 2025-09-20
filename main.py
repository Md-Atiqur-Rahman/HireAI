
from src.feature.multiple_resume_analyzer.multiple_rezume_analyze import multiple_resume_analysis
from src.database.db_job_requirements import init_db
from src.Admin.job_category_page import job_category_page
from src.Admin.job_requirment import job_requirements_page

# In main.py or upload_resume.py
from src.feature.resume_analyzer.single_resume_analyzer import resume_uploader

init_db()
import streamlit as st

# Sidebar navigation
from streamlit_option_menu import option_menu

with st.sidebar:
    page = option_menu(
        menu_title="Navigation",
        options=["Single Resume Analysis","Multiple Resume Analysis", "Job Requirements", "Job Categories"],
        icons=["file-earmark-text","file-earmark-text", "list-task", "folder"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical"
    )

# Load the appropriate page
if page == "Single Resume Analysis":
    resume_uploader()
elif page == "Multiple Resume Analysis":
    multiple_resume_analysis()
elif page == "Job Requirements":
    job_requirements_page()
elif page == "Job Categories":
    job_category_page()

    
