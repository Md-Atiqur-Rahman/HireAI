import streamlit as st

from src.feature.dataclasses.Score import Score

def ranked_candidates_by_Score_table(df,total_records):
    per_page = 5
    total_pages = (total_records // per_page) + (1 if total_records % per_page else 0)
    offset = (st.session_state.current_page - 1) * per_page
    # --- Table Header ---
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("🏆 Ranked Candidates by Score")
    with col3:
         # --- Download CSV ---
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download as CSV",
            data=csv,
            file_name=f"resume_analysis_page{st.session_state.current_page}.csv",
            mime="text/csv",
        )


    col_sizes = [1, 3, 3, 2, 2, 2]  # Rank, Candidate, Email, Experience, Score, Action
    columns = st.columns(col_sizes)
    headers = ["Rank", "Candidate", "Email", "Experience", "Score", "Action"]
    for col, header in zip(columns, headers):
        col.markdown(f"**{header}**")

    # --- Table Rows with Inline Expand using "View" button ---
    for _, row in df.iterrows():
        cols = st.columns(col_sizes)
        rank = row["Rank"]
        cols[0].write(rank)
        cols[1].write(row["Candidate"])
        cols[2].write(row.get("Email", "-"))
        cols[3].write(f"{row.get('Experience', 0)} yrs")
        cols[4].write(f"{row.get('TotalScore', 0)} %")

        # Unique key for this row
        row_key = f"row_{rank}"
        
        # Initialize expanded state for this row
        if row_key not in st.session_state:
            st.session_state[row_key] = False

        # "View" button toggles the expanded state
        if cols[5].button("View", key=f"btn_{row_key}"):
            st.session_state[row_key] = not st.session_state[row_key]

        # If this row is expanded, show the expander
        if st.session_state[row_key]:
            with st.expander(f"📄 Analysis for {row['Candidate']}", expanded=True):
                st.write(f"**Name:** {row['Candidate']}")
                st.write(f"**Score (%):** {row['TotalScore']}")
                st.write(f"**Experience:** {row['Experience']} yrs")
                st.text(row.get('SummaryText', '-'))

  
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.current_page > 1:  # Only show Previous if not first page
            if st.button("⬅️ Previous"):
                st.session_state.current_page -= 1
                st.rerun()

    with col3:
        if st.session_state.current_page < total_pages:  # Only show Next if not last page
            if st.button("Next ➡️"):
                st.session_state.current_page += 1
                st.rerun()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.text(f"Page {st.session_state.current_page} of {total_pages}")
    with col3:
         st.text(f"Total Records-{total_records}")




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


def candidate_scores_table(df, total_records):
    """
    Display candidate scores in a Streamlit table with pagination and expandable details.
    """
    df['Status'] = df['TotalScore'].apply(
    lambda x: "Highly Qualified" if x >= 85 else
              "Qualified" if x >= 60 else
              "Not Qualified"
)

    # --- Pagination ---
    per_page = 5
    total_pages = (total_records // per_page) + (1 if total_records % per_page else 0)
    offset = (st.session_state.current_page - 1) * per_page

    # --- Table Header ---
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("📊 Candidate Scores Summary")
    with col3:
         # --- Download CSV ---
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download as CSV",
            data=csv,
            file_name=f"resume_analysis_page{st.session_state.current_page}.csv",
            mime="text/csv",
            key=f"download_csv_page_{st.session_state.current_page}"  # unique key
        )

    # --- Table Columns ---
    col_sizes = [2, 2, 2, 2, 2, 2, 2,2]  # Candidate, Experience, Education, Tech, Others, Final, Status
    headers = ["Candidate", "Experience (%)", "Education (%)", "Technical Skills (%)",
               "Others (%)", "Final Score (%)", "Status","Action"]

    cols = st.columns(col_sizes)
    for col, header in zip(cols, headers):
        col.markdown(f"**{header}**")

    # --- Table Rows ---
    for i, row in df.iterrows():
        cols = st.columns(col_sizes)
        cols[0].write(row["Candidate"])
        cols[1].markdown(format_score(row.get("ExperienceScore", 0)), unsafe_allow_html=True)
        cols[2].markdown(format_score(row.get("EducationScore", 0)), unsafe_allow_html=True)
        cols[3].markdown(format_score(row.get("TechnicalSkillsScore", 0)), unsafe_allow_html=True)
        cols[4].markdown(format_score(row.get("OthersScore", 0)), unsafe_allow_html=True)
        cols[5].markdown(format_score(row.get("TotalScore", 0)), unsafe_allow_html=True)
        cols[6].write(row.get("Status", "Pending"))

        # --- Expandable details ---
        row_key = f"row_{i}"
        if row_key not in st.session_state:
            st.session_state[row_key] = False
        if cols[7].button("View", key=f"score_btn_{row_key}"):
            st.session_state[row_key] = not st.session_state[row_key]
        if st.session_state[row_key]:
            with st.expander(f"📄 Details for {row['Candidate']}", expanded=True):
                st.write(f"**Name:** {row['Candidate']}")
                st.write(f"**Email:** {row.get('Email','-')}")
                st.write(f"**Score (%):** {row.get('TotalScore',0)}")
                st.write(f"**Experience:** {row.get('Experience',0)} yrs")
                st.text(row.get("SummaryText", "-"))

    # --- Pagination Controls ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.current_page > 1:
            if st.button("⬅️ Previous", key=f"prev_page_{st.session_state.current_page}"):
                st.session_state.current_page -= 1
                st.rerun()
    with col3:
        if st.session_state.current_page < total_pages:
            if st.button("Next ➡️", key=f"next_page_{st.session_state.current_page}"):
                st.session_state.current_page += 1
                st.rerun()

    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.text(f"Page {st.session_state.current_page} of {total_pages}")
    with col3:
         st.text(f"Total Records-{total_records}")


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



