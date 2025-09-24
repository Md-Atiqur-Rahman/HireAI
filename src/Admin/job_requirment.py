import streamlit as st
import json
from src.Helper.banner_style import banner_style
from src.database.db_job_category import get_all_categories
from src.database.db_job_requirements import save_job_requirement, get_requirements_by_category


def job_requirements_page():
    banner_style("Job Requirements Management 📝")

    # --- Category selection ---
    categories = get_all_categories()
    selected_category_name = ""
    selected_category_id = 0
    if not categories:
        st.warning("No categories found. Please add a category first.")
        return
    else:
        category_dict = {cat['name']: cat['id'] for cat in categories}
        selected_category_name = st.selectbox("Select Job Category", list(category_dict.keys()))
        selected_category_id = category_dict[selected_category_name]

    # --- Session state init ---
    for key in ["experience_reqs", "education_reqs", "tech_skills", "other_reqs"]:
        if key not in st.session_state:
            st.session_state[key] = []

    # ---- Experience Section ----
    with st.expander("➕ Add Experience Requirement"):
        years_input = st.text_input("Years of Experience", placeholder="e.g., 3, 3+, 3-5")
        new_subject = st.text_input("Add Technology / Subject", key="subject_input")
        if st.button("➕ Add Experience"):
            if years_input.strip() and new_subject.strip():
                text = f"{selected_category_name} with {years_input} years of experience in {new_subject}"
                st.session_state.experience_reqs.append(text)
                st.success(f"Added: {text}")
            else:
                st.error("Please enter valid years & subject")

        if st.session_state.experience_reqs:
            st.write("Current experience requirements:")
            for exp in st.session_state.experience_reqs:
                st.markdown(f"- {exp}")

    # ---- Education Section ----
    with st.expander("➕ Add Education Requirement"):
        degree = st.selectbox("Degree", ["Bachelor’s", "Master’s", "PhD", "Other"])
        field = st.text_input("Field of Study (e.g., Computer Science, Engineering)")
        if st.button("➕ Add Education"):
            text = f"{degree} degree in {field}" if field.strip() else f"{degree} degree"
            st.session_state.education_reqs.append(text)
            st.success(f"Added: {text}")

        if st.session_state.education_reqs:
            st.write("Current education requirements:")
            for edu in st.session_state.education_reqs:
                st.markdown(f"- {edu}")

    # ---- Skills Section ----
    with st.expander("➕ Add Technical Skill"):
        skill = st.text_input("Skill / Tool (e.g., Docker, Kubernetes, TensorFlow)")
        if st.button("➕ Add Skill"):
            if skill.strip():
                st.session_state.tech_skills.append(skill.strip())
                st.success(f"Added: {skill}")
            else:
                st.error("Enter a valid skill")

        if st.session_state.tech_skills:
            st.write("Current technical skills:")
            for sk in st.session_state.tech_skills:
                st.markdown(f"- {sk}")

    # ---- Others Section ----
    with st.expander("➕ Add Other Requirement"):
        custom_req = st.text_area("Custom Requirement")
        if st.button("➕ Add Other"):
            if custom_req.strip():
                st.session_state.other_reqs.append(custom_req.strip())
                st.success(f"Added: {custom_req}")
            else:
                st.error("Requirement cannot be empty")

        if st.session_state.other_reqs:
            st.write("Current other requirements:")
            for o in st.session_state.other_reqs:
                st.markdown(f"- {o}")

    # ---- Save to DB ----
    if st.button("💾 Save All Requirements"):
        requirements = {
            "Experience": st.session_state.experience_reqs,
            "Education": st.session_state.education_reqs,
            "TechnicalSkills": st.session_state.tech_skills,
            "Others": st.session_state.other_reqs
        }
        save_job_requirement(selected_category_id, requirements)
        st.success("✅ Requirements saved successfully!")

    # ---- Show Existing ----
    st.subheader(f"📋 Current Requirements for {selected_category_name}")
    updated_reqs = get_requirements_by_category(selected_category_id)

    if updated_reqs:
        for key, values in updated_reqs.items():
            st.markdown(f"**{key}:**")
            if isinstance(values, list):
                for v in values:
                    st.markdown(f"- {v}")
            else:
                st.markdown(f"- {values}")
    else:
        st.info("No requirements added yet.")
