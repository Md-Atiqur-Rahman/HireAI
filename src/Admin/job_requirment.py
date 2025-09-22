import streamlit as st
import json
from src.Helper.banner_style import banner_style
from src.database.db_job_category import get_all_categories
from src.database.db_job_requirements import save_job_requirement, get_requirements_by_category

def job_requirements_page():
    # st.title("📝 Job Requirements Management")
    banner_style("Job Requirements Management 📝")
    categories = get_all_categories() 
    selected_category_name="";
    selected_category_id = 0;
    if not categories:
        st.warning("No categories found. Please add a category first.")
    else:
        category_dict = {cat['name']: cat['id'] for cat in categories} 
        selected_category_name = st.selectbox("Select Job Category", list(category_dict.keys()))
        selected_category_id = category_dict[selected_category_name]

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

        

    # ---- Education Section ----
    with st.expander("➕ Add Education Requirement"):
        degree = st.selectbox("Degree", ["Bachelor’s", "Master’s", "PhD", "Other"])
        field = st.text_input("Field of Study (e.g., Computer Science, Engineering)")
        

    # ---- Skills Section ----
    with st.expander("➕ Add Skill Requirement"):
        skill = st.text_input("Skill / Tool (e.g., Docker, Kubernetes, TensorFlow)")


    # ---- Freeform Section ----
    st.subheader("✍️ Add Custom Requirement")
    custom_req = st.text_area("Custom Requirement")
        

    # Save experience requirement
    if st.button("Save Experience Requirement"):
        exp = ""
        edu = ""
        tech = ""
        others =""
        
        if not years_input.strip():
            st.error("Please enter years of experience")
        elif not st.session_state.subjects:
            st.error("Please add at least one subject")

        subjects_text = " / ".join(st.session_state.subjects)
        exp = f"{selected_category_name} with {years_input} years of experience in {subjects_text}"
        st.session_state.subjects = []  # reset subjects after save

        # Education
        edu = f"{degree} degree in {field}" if field.strip() else f"{degree} degree"

        if skill.strip():
            tech = f"Experience with {skill}"
        else:
            st.error("⚠️ Please enter a skill")

        if custom_req.strip():
            others =custom_req.strip()
        else:
            st.error("⚠️ Requirement cannot be empty")
        
        requirements = {
            "Experience": exp.strip(),
            "Education": edu.strip(),
            "TechnicalSkills": tech.strip(),
            "Skills": tech.strip(),
            "Others": others.strip()
        }
        save_job_requirement(selected_category_id, requirements)
        st.success("✅ Requirements saved successfully!")

# ---------------- Show Existing Requirements ----------------
# ---------------- Show Existing Requirements ----------------
    st.subheader(f"📋 Current Requirements for {selected_category_name}")
    updated_reqs = get_requirements_by_category(selected_category_id)

    if updated_reqs:
        for key, value in updated_reqs.items():
            st.markdown(f"**{key}:** {value if value else '-'}")
    else:
        st.info("No requirements added yet.")


