import streamlit as st
import json
from src.db import get_all_requirements, save_job_requirement, get_requirements_by_category

def job_requirements_page():
    st.title("📝 Job Requirements Management")

    # Dropdown for category
    category = st.selectbox("Select Job Category", ["Software Engineer", "Data Engineer", "AI Specialist", "Custom" , "Custom1","Data Science"])

    st.subheader("Add Structured Requirements")

    # ---- Experience Section ----
    with st.expander("➕ Add Experience Requirement"):
        years = st.number_input("Years of Experience", min_value=1, max_value=50, step=1)
        subject = st.text_input("Technology / Subject (e.g., C#, Python, SQL)")
        add_exp = st.button("➕ Add Experience Requirement")

        if add_exp:
            if subject.strip():
                req_text = f"{years} years of experience in {subject}"
                save_job_requirement(category, [req_text])   # Save into DB
                st.success(f"Added: {req_text}")
            else:
                st.error("⚠️ Please enter at least one subject")

    # ---- Education Section ----
    with st.expander("➕ Add Education Requirement"):
        degree = st.selectbox("Degree", ["Bachelor’s", "Master’s", "PhD", "Other"])
        field = st.text_input("Field of Study (e.g., Computer Science, Engineering)")
        add_edu = st.button("➕ Add Education Requirement")

        if add_edu:
            req_text = f"{degree} degree in {field}" if field.strip() else f"{degree} degree"
            save_job_requirement(category, [req_text])
            st.success(f"Added: {req_text}")

    # ---- Skills Section ----
    with st.expander("➕ Add Skill Requirement"):
        skill = st.text_input("Skill / Tool (e.g., Docker, Kubernetes, TensorFlow)")
        add_skill = st.button("➕ Add Skill Requirement")

        if add_skill:
            if skill.strip():
                req_text = f"Experience with {skill}"
                save_job_requirement(category, [req_text])
                st.success(f"Added: {req_text}")
            else:
                st.error("⚠️ Please enter a skill")

    # ---- Freeform Section ----
    st.subheader("✍️ Add Custom Requirement")
    custom_req = st.text_area("Custom Requirement")
    if st.button("➕ Add Custom Requirement"):
        if custom_req.strip():
            save_job_requirement(category, [custom_req.strip()])
            st.success(f"Added: {custom_req.strip()}")
        else:
            st.error("⚠️ Requirement cannot be empty")

    # ---- Show Existing Requirements ----
    st.subheader(f"📋 Current Requirements for {category}")
    requirements = get_requirements_by_category(category)

    if requirements:
        for i, req in enumerate(requirements, 1):
            st.markdown(f"{i}. {req}")
    else:
        st.info("No requirements added yet.")

