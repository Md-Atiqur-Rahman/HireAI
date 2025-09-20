
from src.feature.multiple_resume_analyzer.dashboard import dashboard_page
from src.database.db_job_category import create_category_table
from src.database.db_config import drop_table
from src.database.db_candidates import create_candidates_table
from src.feature.multiple_resume_analyzer.multiple_rezume_analyze import multiple_resume_analysis
from src.database.db_job_requirements import create_job_requirements_table
from src.Admin.job_category_page import job_category_page
from src.Admin.job_requirment import job_requirements_page

# In main.py or upload_resume.py
from src.feature.resume_analyzer.single_resume_analyzer import resume_uploader

# drop_table("job_requirements")
# drop_table("job_categories")

create_job_requirements_table()
create_candidates_table()
create_category_table()

import streamlit as st

# Sidebar navigation
from streamlit_option_menu import option_menu

with st.sidebar:
    page = option_menu(
        menu_title="Menu",
        options=["DashBoard","Single Resume Analysis","Multiple Resume Analysis", "Job Requirements", "Job Categories"],
        icons=["file-earmark-text","file-earmark-text", "list-task", "folder"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical"
    )

# Load the appropriate page
if page == "Single Resume Analysis":
    resume_uploader()
elif page == "DashBoard":
    dashboard_page()
elif page == "Multiple Resume Analysis":
    multiple_resume_analysis()
elif page == "Job Requirements":
    job_requirements_page()
elif page == "Job Categories":
    job_category_page()

    
