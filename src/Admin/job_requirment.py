import streamlit as st
import json
from src.Helper.banner_style import banner_style
from src.database.db_job_category import get_all_categories
from src.database.db_job_requirements import save_job_requirement, get_requirements_by_category


# --- Initialize session state ---
# def clear_all_requirements():
#     for key in ["experience_reqs", "education_reqs", "tech_skills", "other_reqs"]:
#         if key not in st.session_state:
#             st.session_state[key] = []
# --- Initialize + Clear helper ---
def clear_all_requirements():
    for key in ["experience_reqs", "education_reqs", "tech_skills", "other_reqs"]:
        st.session_state[key] = []   # সবসময় empty করে দেবে
    # expander flags reset (সব collapse হবে)
    
def collpase_all_expander():
    for key in ["exp_expander", "edu_expander", "skill_expander", "other_expander"]:
        st.session_state[key] = False


# dynamic key counters
def clear_input():
    for k in ["years_input_key","subject_input_key","field_input_key","skills_input_key", "other_input_key"]:
        if k not in st.session_state:
            st.session_state[k] = 0

def job_requirements_page():
    for key in ["experience_reqs", "education_reqs", "tech_skills", "other_reqs"]:
        if key not in st.session_state:
            st.session_state[key] = []
    
    for k in ["years_input_key","subject_input_key","field_input_key","skills_input_key", "other_input_key"]:
        if k not in st.session_state:
            st.session_state[k] = 0

    banner_style("Job Requirements Management 📝")

    # --- Category selection ---
    categories = get_all_categories()
    if not categories:
        st.warning("No categories found. Please add a category first.")
        return

    category_dict = {cat['name']: cat['id'] for cat in categories}
    selected_category_name = st.selectbox("Select Job Category", list(category_dict.keys()))
    selected_category_id = category_dict[selected_category_name]

    

    # ---- Experience Section ----
    # ---- Experience Section ----
    with st.expander("➕ Add Experience Requirement", expanded=st.session_state.get("exp_expander", False)):
        st.session_state["exp_expander"] = True 
        if len(st.session_state.experience_reqs) == 0:
            years_input = st.text_input("Years of Experience", placeholder="e.g., 3, 3+, 3-5",key=f"years_input_{st.session_state.years_input_key}")
            new_subject = st.text_input("Add Technology / Subject",key=f"subject_input_{st.session_state.subject_input_key}")
            if st.button("➕ Add Experience"):
                if years_input.strip() and new_subject.strip():
                    text = f"{selected_category_name} with {years_input} years of experience in {new_subject}"
                    st.session_state.experience_reqs.append(text)
                    st.success(f"Added: {text}")
                    # reset inputs
                    st.session_state.years_input_key += 1
                    st.session_state.subject_input_key += 1
                    st.rerun()
                    st.rerun()
                else:
                    st.error("Please enter valid years & subject")
        else:
            st.info("Only one Experience requirement is allowed. Delete the existing one to add a new.")

        # Display existing Experience requirement(s)
        if st.session_state.experience_reqs:
            for i, exp in enumerate(st.session_state.experience_reqs):
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.markdown(f"- {exp}")
                with col2:
                    if st.button("❌", key=f"exp_del_{i}"):
                        st.session_state.experience_reqs.pop(i)
                        st.success("Deleted!")
                        st.rerun()  # immediately refresh


    # ---- Education Section ----
    with st.expander("➕ Add Education Requirement", expanded=st.session_state.get("edu_expander", False)):
        st.session_state["edu_expander"] = True 
        degree = st.selectbox("Degree", ["Bachelor’s", "Master’s", "PhD", "Other"])
        field = st.text_input("Field of Study (e.g., Computer Science, Engineering)",key=f"field_input_{st.session_state.field_input_key}")
        
        if st.button("➕ Add Education"):
            text = f"{degree} degree in {field}" if field.strip() else f"{degree} degree"
            st.session_state.education_reqs.append(text)
            st.success(f"Added: {text}")
            # reset inputs
            st.session_state.field_input_key += 1
            st.rerun()
        


        for i, edu in enumerate(st.session_state.education_reqs):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"- {edu}")
            with col2:
                if st.button("❌", key=f"edu_del_{i}"):
                    st.session_state.education_reqs.pop(i)
                    st.success("Deleted!")
                    st.rerun()

    # ---- Technical Skills Section ----
    with st.expander("➕ Add Technical Skill", expanded=st.session_state.get("skill_expander", False)):
        st.session_state["skill_expander"] = True 
        skill = st.text_input("Skill / Tool (e.g., Docker, Kubernetes, TensorFlow)",key=f"skills_input_{st.session_state.skills_input_key}")
        if st.button("➕ Add Skill"):
            if skill.strip():
                st.session_state.tech_skills.append(skill.strip())
                st.success(f"Added: {skill}")
                # reset inputs
                st.session_state.skills_input_key += 1
                st.rerun()
            else:
                st.error("Enter a valid skill")

        for i, sk in enumerate(st.session_state.tech_skills):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"- {sk}")
            with col2:
                if st.button("❌", key=f"sk_del_{i}"):
                    st.session_state.tech_skills.pop(i)
                    st.success("Deleted!")
                    st.rerun()

    # ---- Others Section ----other_input_key
    with st.expander("➕ Add Other Requirement", expanded=st.session_state.get("other_expander", False)):
        st.session_state["other_expander"] = True 
        # custom_req = st.text_area("Custom Requirement",key=f"other_input_{st.session_state.other_input_key}")
        custom_req = st.text_input("Others Requirement",key=f"other_input_{st.session_state.other_input_key}")
        
        if st.button("➕ Add Other"):
            if custom_req.strip():
                st.session_state.other_reqs.append(custom_req.strip())
                st.success(f"Added: {custom_req}")
                # reset inputs
                st.session_state.other_input_key += 1
                st.rerun()
            else:
                st.error("Requirement cannot be empty")

        for i, o in enumerate(st.session_state.other_reqs):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"- {o}")
            with col2:
                if st.button("❌", key=f"other_del_{i}"):
                    st.session_state.other_reqs.pop(i)
                    st.success("Deleted!")
                    st.rerun()

    # ---- Save to DB ----
    if st.button("💾 Save All Requirements"):
        # validation checks
        collpase_all_expander()
        if not st.session_state.experience_reqs:
            st.warning("⚠️ Please add at least one Experience requirement before saving.")
        elif not st.session_state.education_reqs:
            st.warning("⚠️ Please add at least one Education requirement before saving.")
        elif not st.session_state.tech_skills:
            st.warning("⚠️ Please add at least one Technical Skill before saving.")
        elif not st.session_state.other_reqs:
            st.warning("⚠️ Please add at least one Other requirement before saving.")
        else:
            requirements = {
                "Experience": st.session_state.experience_reqs,
                "Education": st.session_state.education_reqs,
                "TechnicalSkills": st.session_state.tech_skills,
                "Others": st.session_state.other_reqs
            }
            print("requirements--------->",json.dumps(requirements))
            # save_job_requirement(selected_category_id, requirements)
            st.success("✅ Requirements saved successfully!")
            clear_all_requirements()
            collpase_all_expander()
            st.rerun()

    # ---- Show Existing from DB ----
    # ---- Show Existing from DB ----
    st.subheader(f"📋 Current Requirements for {selected_category_name}")
    updated_reqs = get_requirements_by_category(selected_category_id)

    # Only display if there is at least one non-empty category
    if any(updated_reqs.get(k) for k in ["Experience", "Education", "TechnicalSkills", "Others"]):
        for key in ["Experience", "Education", "TechnicalSkills", "Others"]:
            values = updated_reqs.get(key)
            if values:  # only show non-empty categories
                st.markdown(f"**{key}:**")
                for v in values:
                    st.markdown(f"- {v}")
    else:
        st.info("No requirements added yet.")
