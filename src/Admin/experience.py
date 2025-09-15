import streamlit as st
from src.db import save_job_requirement

def experience_section(category):
    st.subheader("➕ Add Experience Requirement")

    # Years input
    years_input = st.text_input("Years of Experience", placeholder="e.g., 3, 3+, 3-5", key="years_input")

    # Initialize subjects in session state
    if "subjects" not in st.session_state:
        st.session_state.subjects = []
    if "new_subject_input" not in st.session_state:
        st.session_state.new_subject_input = ""

    # Subject input
    new_subject = st.text_input(
        "Add Technology / Subject",
        value=st.session_state.new_subject_input,
        key="new_subject_input",
        placeholder="e.g., C#, Python, SQL"
    )

    # Add subject button
    if st.button("➕ Add Subject"):
        if new_subject.strip():
            if new_subject.strip() not in st.session_state.subjects:
                st.session_state.subjects.append(new_subject.strip())
                st.success(f"Added subject: {new_subject.strip()}")
            else:
                st.warning(f"{new_subject.strip()} already added")
            # Clear input safely using session_state
            st.session_state.new_subject_input = ""
        else:
            st.error("Enter a valid subject")

    # Display current subjects
    if st.session_state.subjects:
        st.write("Current subjects:", " / ".join(st.session_state.subjects))

    # Save experience requirement
    if st.button("💾 Save Experience Requirement"):
        if not years_input.strip():
            st.error("Please enter years of experience")
        elif not st.session_state.subjects:
            st.error("Please add at least one subject")
        else:
            subjects_text = " / ".join(st.session_state.subjects)
            req_text = f"{category} with {years_input} years of experience in {subjects_text}"
            save_job_requirement(category, [req_text])
            st.success(f"Saved: {req_text}")
            st.session_state.subjects = []  # reset subjects after save
            st.session_state.new_subject_input = ""  # reset input
