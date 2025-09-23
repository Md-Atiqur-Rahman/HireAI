

from src.database.db_job_category import get_all_categories
import plotly.express as px
import streamlit as st


def candidate_score_vs_experience(df):
    col1, col2 = st.columns([2, 2])  # center column wider 
    with col1:
        # --- Candidate Score Distribution ---
        st.subheader("📈 Candidate Score Distribution")
        fig_score = px.histogram(df, x="TotalScore", nbins=10, title="Score Distribution")
        st.plotly_chart(fig_score, use_container_width=True)
    with col2:
        # --- Experience vs Score Scatter ---
        st.subheader("📊 Experience vs Score")
        categories = get_all_categories()
        categories_map = {c["id"]: c["name"] for c in categories}  # {id: name}

        # Add Category name column to your DataFrame
        df["Category"] = df["CategoryId"].map(categories_map)

        # Now your scatter plot can use 'Category' for color
        fig_exp = px.scatter(
            df,
            x="Experience",
            y="TotalScore",
            color="Category",  # now exists in df
            hover_data=["Candidate"]
        )

        st.plotly_chart(fig_exp, use_container_width=True)

    # --- Score Comparison Chart ---
    # st.subheader("📊 Score Comparison")
    # fig = px.bar(df, x="Candidate", y="TotalScore", color="Candidate", title="Score per Candidate")
    # st.plotly_chart(fig)