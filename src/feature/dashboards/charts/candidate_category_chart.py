
import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.db_candidates import get_candidates_group_by_category

def show_chart_candidate_by_category(df,selected_category_id):
    if df is None or df.empty:
        st.warning("No data available for chart.")
        return
    
    col1, col2 = st.columns([2, 2])  # center column wider

    with col1:
    # --- Candidates per Category ---
        st.subheader("🏷️ Candidates per Category")
        df_cat = pd.DataFrame(get_candidates_group_by_category(selected_category_id), columns=["CategoryName", "total_candidates"])
        fig_cat = px.pie(df_cat, names="CategoryName", values="total_candidates")
        st.plotly_chart(fig_cat, use_container_width=True)
    with col2:
            # --- Top Candidates Bar Chart ---
        st.subheader("🏆 Top Candidates by Score")
        top_df = df.sort_values(by="TotalScore", ascending=False)
        fig_top = px.bar(top_df, x="Candidate", y="TotalScore", color="TotalScore")
        st.plotly_chart(fig_top, use_container_width=True)

    