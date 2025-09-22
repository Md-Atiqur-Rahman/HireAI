import streamlit as st

from src.Helper.banner_style import banner_style
from src.database.db_job_category import create_category_table, get_all_categories, save_job_category




# -------------------
# Streamlit page
# -------------------
def job_category_page():
    # st.title("📂 Job Category Management")
    banner_style("Job Category Management 🏷️")
    # Ensure table exists
    create_category_table()

    # Add new category
    st.subheader("➕ Add New Job Category")
    new_category = st.text_input("Category Name", placeholder="e.g., Software Engineer")
    if st.button("Add Category"):
        if new_category.strip():
            save_job_category(new_category.strip())
        else:
            st.error("Category name cannot be empty")

    # Show existing categories
    st.subheader("📋 Existing Categories")
    categories = get_all_categories()
    if categories:
        for i, cat in enumerate(categories, 1):
            st.write(f"{i}. {cat['name']}")
    else:
        st.info("No job categories found yet.")
    

