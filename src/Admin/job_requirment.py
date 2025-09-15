import streamlit as st
from src.db import init_db, save_requirement, get_requirements_by_category

def job_requirements():
    init_db()

    st.title("Job Requirement Management")

    category = st.text_input("Category")
    requirements_text = st.text_area("Enter requirements (one per line)")

    if st.button("Save"):
        if category.strip() and requirements_text.strip():
            requirements_list = [r.strip() for r in requirements_text.split("\n") if r.strip()]
            save_requirement(category, requirements_list)
            st.success("Requirements saved successfully!")

    # Show existing categories
    st.subheader("Existing Job Requirement Categories")
    conn_reqs = get_requirements_by_category(category)
    for r in conn_reqs:
        st.write(f"- {r}")
