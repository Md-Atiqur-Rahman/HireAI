import re
from dateutil import parser
from datetime import datetime
import spacy
from sentence_transformers import SentenceTransformer, util
import torch

from src.Admin.job_requirment import job_requirements_page
from src.Helper.parser import extract_text_from_pdf

# In main.py or upload_resume.py
from src.db import  init_db
from src.upload_resume import resume_uploader

init_db()
import streamlit as st

st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("Resume Analyzer Application")

# Sidebar navigation
from streamlit_option_menu import option_menu

with st.sidebar:
    page = option_menu(
        menu_title="Navigation",
        options=["Resume Analysis", "Job Requirements"],
        icons=["file-earmark-text", "list-task"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",  # vertical sidebar
    )


# Load the appropriate page
if page == "Resume Analysis":
    resume_uploader()

elif page == "Job Requirements":
    job_requirements_page()

