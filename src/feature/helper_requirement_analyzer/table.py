import random
import streamlit as st

from src.database.db_candidates import get_candidates_paginated
from src.feature.dataclasses.Score import Score



import streamlit as st
import pandas as pd


def format_score(score):
    if score >= 80:
        color = "#2ca02c"  # green
        icon = "✅"
    elif score >= 50:
        color = "#ff7f0e"  # yellow/orange
        icon = "⚠️"
    else:
        color = "#d62728"  # red
        icon = "❌"

    return f"<div style='font-weight:bold; font-size:18px; color:{color}'>{score} {icon}</div>"


def candidate_scores_table(selected_category_id, per_page, total_records,total_pages_scores):
    """
    Display candidate scores in a Streamlit table with pagination and expandable details.
    """

    offset_Scores = (st.session_state.page_scores_summary - 1) * per_page
    candidates_Scores = get_candidates_paginated(selected_category_id, per_page, offset_Scores)
    df = pd.DataFrame(candidates_Scores)
    df["Rank"] = range(offset_Scores + 1, offset_Scores + len(df) + 1)
    if df.empty:
        st.info("No candidate data found.")
        return

    # --- Table Header ---
    if df.empty:
        st.warning("No candidate scores available.")
        return
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("📊 Candidate Scores Summary")

    # --- Table Columns ---
    col_sizes = [1,2, 2, 2, 2, 2, 2, 2]  # Candidate, Experience, Education, Tech, Others, Final, Status
    headers = ["Rank", "Candidate", "Experience (%)", "Education (%)", "Technical Skills (%)",
               "Others (%)", "Final Score (%)", "Status"
               ]

    cols = st.columns(col_sizes)
    for col, header in zip(cols, headers):
        col.markdown(f"**{header}**")

    # --- Table Rows ---
    for i, row in df.iterrows():
        cols = st.columns(col_sizes)
        rank = row["Rank"]
        cols[0].write(rank)
        cols[1].write(row["Candidate"])
        cols[2].markdown(format_score(row.get("ExperienceScore", 0)), unsafe_allow_html=True)
        cols[3].markdown(format_score(row.get("EducationScore", 0)), unsafe_allow_html=True)
        cols[4].markdown(format_score(row.get("TechnicalSkillsScore", 0)), unsafe_allow_html=True)
        cols[5].markdown(format_score(row.get("OthersScore", 0)), unsafe_allow_html=True)
        cols[6].markdown(format_score(row.get("TotalScore", 0)), unsafe_allow_html=True)
        cols[7].write(row.get("Status", "Pending"))
        

    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.session_state.page_scores_summary > 1:
            if st.button("⬅️ Previous", key="prev_scores"):
                st.session_state.page_scores_summary -= 1
                st.rerun()
    with col3:
        if st.session_state.page_scores_summary < total_pages_scores:
            if st.button("Next ➡️", key="next_scores"):
                st.session_state.page_scores_summary += 1
                st.rerun()
    with col2:
        st.text(f"Page {st.session_state.page_scores_summary} of {total_pages_scores} | Total Records: {total_records}")
    st.markdown("---")

    return df;  


import streamlit as st

def display_grouped_results(df_grouped):
    """
    Displays a grouped results table with expanders for each requirement,
    showing KeywordsMatched, SemanticMatches, MissingRequirements, and MatchPercent.
    """
    if df_grouped.empty:
        st.warning("No results to display.")
        return

    # Group by Category
    categories = df_grouped["Category"].unique()
    
    for cat in categories:
        st.subheader(f"📂 {cat} Requirements")
        cat_df = df_grouped[df_grouped["Category"] == cat]
        
        # Table header
        col_sizes = [3, 2, 2, 2, 1]  # Requirement, KeywordsMatched, SemanticMatches, MissingRequirements, Match %
        headers = ["Requirement", "KeywordsMatched", "SemanticMatches", "MissingRequirements", "Match %"]
        cols = st.columns(col_sizes)
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        # Table rows
        for idx, row in cat_df.iterrows():
            cols = st.columns(col_sizes)
            cols[0].write(row["Requirement"])
            cols[1].write(row["KeywordsMatched"] if row["KeywordsMatched"] else "-")
            cols[2].write(row["SemanticMatches"] if row["SemanticMatches"] else "-")
            cols[3].write(row["MissingRequirements"] if row["MissingRequirements"] else "-")
            cols[4].write(f"{row['MatchPercent']} %")

        st.markdown("---")



