import streamlit as st
import json
from src.DB.Scripts.job_category import get_all_categories
from src.db import get_all_requirements, save_job_requirement, get_requirements_by_category

def job_requirements_page():
    st.title("📝 Job Requirements Management")

    # Dropdown for category
    categories = get_all_categories()
    # Dropdown for category
    category = st.selectbox("Select Job Category", categories)
    st.subheader("Add Structured Requirements")

    # ---- Experience Section ----
    with st.expander("➕ Add Experience Requirement"):
            # Input for year(s)
        years_input = st.text_input("Years of Experience", placeholder="e.g., 3, 3+, 3-5")
        if 'subjects' not in st.session_state:
            st.session_state.subjects = []
        new_subject = st.text_input("Add Technology / Subject", key="subject_input")
        if st.button("➕ Add Subject"):
            if new_subject.strip():
                st.session_state.subjects.append(new_subject.strip())
                st.success(f"Added subject: {new_subject}")
            else:
                st.error("Enter a valid subject")

        # Display current subjects
        if st.session_state.subjects:
            st.write("Current subjects:", " / ".join(st.session_state.subjects))

        # Save experience requirement
        if st.button("Save Experience Requirement"):
            if not years_input.strip():
                st.error("Please enter years of experience")
            elif not st.session_state.subjects:
                st.error("Please add at least one subject")
            else:
                subjects_text = " / ".join(st.session_state.subjects)
                req_text = f"{category} with {years_input} years of experience in {subjects_text}"
                save_job_requirement(category, req_text)
                st.success(f"Saved: {req_text}")
                st.session_state.subjects = []  # reset subjects after save

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
    print(requirements)
    if requirements:
        for i, req in enumerate(requirements, 1):
            st.markdown(f"{i}. {req}")
    else:
        st.info("No requirements added yet.")


# # Existing requirements
#     st.subheader("📂 Existing Job Requirement Categories")
#     existing_reqs = get_all_requirements()  # ✅ fetch everything

#     if existing_reqs:
#         # Group by category
#         categories = {}
#         for row in existing_reqs:
#             cat = row["category"]
#             req = row["requirement"]
#             categories.setdefault(cat, []).append(req)

#         # Show each category with its requirements
#         for cat, reqs in categories.items():
#             st.markdown(f"**{cat}**")
#             for r in reqs:
#                 st.write(f"- {r}")
#     else:
#         st.info("No job requirements saved yet.")
