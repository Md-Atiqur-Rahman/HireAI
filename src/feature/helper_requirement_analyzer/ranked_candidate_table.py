import random
import pandas as pd
import streamlit as st

from src.database.db_candidates import get_candidates_paginated
def ranked_candidates_by_Score_table(selected_category_id,per_page,total_records,total_pages_scores):
    
    offset_ranked = (st.session_state.page_ranked_candidates - 1) * per_page
    candidates_ranked = get_candidates_paginated(selected_category_id, per_page, offset_ranked)
    df = pd.DataFrame(candidates_ranked)
    df["Rank"] = range(offset_ranked + 1, offset_ranked + len(df) + 1)
    if df.empty:
        st.info("No candidate data found.")
        return
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
        if st.session_state.page_ranked_candidates > 1:
            if st.button("⬅️ Previous", key="prev_ranked"):
                st.session_state.page_ranked_candidates -= 1
                st.rerun()
    with col3:
        if st.session_state.page_ranked_candidates < total_pages_scores:
            if st.button("Next ➡️", key="next_ranked"):
                st.session_state.page_ranked_candidates += 1
                st.rerun()
    with col2:
        st.text(f"Page {st.session_state.page_ranked_candidates} of {total_pages_scores} | Total Records: {total_records}")

    return df;  




