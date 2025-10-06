import pandas as pd
from src.database.db_config import get_connection

def get_candidate_summary():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM candidate_requirements", conn)
    conn.close()

    # Aggregate per candidate
    summary_rows = []
    for candidate_email, group in df.groupby("candidate_email"):
        candidate_name = group['candidate_email'].iloc[0]  # or join with candidates table to get name
        keywords_matched = group['keywords_matched'].apply(lambda x: len(x.split(", ")) if x else 0).sum()
        semantic_matches = group['semantic_matches'].apply(lambda x: len(x.split(", ")) if x else 0).sum()
        missing_reqs = group['missing_requirements'].apply(lambda x: len(x.split(", ")) if x else 0).sum()
        match_percent = round(keywords_matched / (keywords_matched + missing_reqs) * 100, 1) if (keywords_matched + missing_reqs) > 0 else 0

        summary_rows.append({
            "Candidate": candidate_name,
            "Keywords Matched": keywords_matched,
            "Semantic Matches": semantic_matches,
            "Missing Requirements": missing_reqs,
            "Match %": match_percent
        })

    return pd.DataFrame(summary_rows)

import streamlit as st
import pandas as pd
from src.database.db_config import get_connection

def get_raw_candidate_data():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT c.Candidate, cr.*
        FROM candidate_requirements cr
        JOIN candidates c ON cr.candidate_email = c.Email
        ORDER BY c.Candidate, cr.Category
    """, conn)
    conn.close()
    return df


def candidate_match_summary_scores(df_raw):
    """
    Aggregate candidate match data into numeric scores per candidate
    and display as paginated table.
    """
    if df_raw.empty:
        st.warning("No candidate match data found.")
        return

    # Ensure numeric columns
    for col in ["keywords_matched", "semantic_matches", "missing_requirements", "match_percent"]:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce").fillna(0)

    # Aggregate per candidate
    df_agg = df_raw.groupby("candidate_email").agg({
        "keywords_matched": "sum",
        "semantic_matches": "sum",
        "missing_requirements": "sum",
        "match_percent": "mean"
    }).reset_index()

    # Round match percent
    df_agg["match_percent"] = df_agg["match_percent"].round(2)

    # Optional: rename for display
    df_agg = df_agg.rename(columns={
        "candidate_email": "Candidate",
        "keywords_matched": "Keywords Matched",
        "semantic_matches": "Semantic Matches",
        "missing_requirements": "Missing Requirements",
        "match_percent": "Match %"
    })

    # --- Pagination ---
    per_page = 5
    total_records = len(df_agg)
    total_pages = (total_records // per_page) + (1 if total_records % per_page else 0)

    if "current_page_match" not in st.session_state:
        st.session_state.current_page_match = 1

    start_idx = (st.session_state.current_page_match - 1) * per_page
    end_idx = start_idx + per_page

    display_df = df_agg[start_idx:end_idx]

    st.subheader("📊 Candidate Match Summary (Scores)")
    st.table(display_df)

    # --- Pagination controls ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.current_page_match > 1:
            if st.button("⬅️ Previous", key="prev_match_page"):
                st.session_state.current_page_match -= 1
                st.experimental_rerun()
    with col3:
        if st.session_state.current_page_match < total_pages:
            if st.button("Next ➡️", key="next_match_page"):
                st.session_state.current_page_match += 1
                st.experimental_rerun()

    st.text(f"Page {st.session_state.current_page_match} of {total_pages}")
    st.text(f"Total Candidates: {total_records}")


import streamlit as st
import pandas as pd
import streamlit as st
import math

def candidate_match_summary_table(df_agg,per_page):
    """
    Display candidate match summary in a paginated, category-wise table.
    Columns: Candidate | Keywords Matched | Semantic Matches | Missing Requirements | Match %
    """
    if df_agg is None or df_agg.empty:
        st.warning("No candidate match summary available.")
        return

    # --- Pagination settings ---
    total_records_match = len(df_agg)
    total_pages_match = math.ceil(total_records_match / per_page)
    offset_match = (st.session_state.page_match_summary - 1) * per_page
    df_match_paginated = df_agg.iloc[offset_match:offset_match+per_page]

    if not df_match_paginated.empty:
        df_match_paginated["Rank"] = range(
            offset_match + 1,
            offset_match + len(df_match_paginated) + 1
        )

    df_match_paginated["Rank"] = range(offset_match + 1, offset_match + len(df_match_paginated) + 1)

    # --- Table Header ---
    col1, col2,  = st.columns([3, 1])
    with col1:
        st.subheader("📊 Candidate Match Summary")
    # with col3:
    #     # Download CSV for current page
    #     csv = df_match_paginated.to_csv(index=False).encode("utf-8")
    #     st.download_button(
    #         "📥 Download CSV",
    #         data=csv,
    #         file_name=f"candidate_match_page{st.session_state.page_match_summary}.csv",
    #         mime="text/csv",
    #         key=f"download_csv_{st.session_state.page_match_summary}"
    #     )

    # --- Table column sizes & headers ---
    col_sizes = [1, 2, 2, 2, 2, 1]
    headers = ["Rank", "Candidate", "Keywords Matched", "Semantic Matches", "Missing Requirements", "Match %"]
    cols = st.columns(col_sizes)
    for col, header in zip(cols, headers):
        col.markdown(f"**{header}**")

    # --- Table rows ---
    for idx, row in df_match_paginated.iterrows():
        cols = st.columns(col_sizes)
        rank = row["Rank"]
        cols[0].write(rank)
        cols[1].write(row["Candidate"])
        cols[2].write(row["KeywordsMatched"])
        cols[3].write(row["SemanticMatches"])
        cols[4].write(row["MissingRequirements"])
        cols[5].write(f"{row['MatchPercent']:.2f} %")

    st.markdown("---")

    # --- Pagination Controls ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.page_match_summary > 1:
            if st.button("⬅️ Previous", key="prev_match"):
                st.session_state.page_match_summary -= 1
                st.rerun()
    with col3:
        if st.session_state.page_match_summary < total_pages_match:
            if st.button("Next ➡️", key="next_match"):
                st.session_state.page_match_summary += 1
                st.rerun()
    with col2:
        st.text(f"Page {st.session_state.page_match_summary} of {total_pages_match} | Total Records: {total_records_match}")
    st.markdown("---")

    return df_match_paginated




import streamlit as st
import pandas as pd

import pandas as pd

def candidate_match_summary_aggregated(df_raw):
    if df_raw is None or df_raw.empty:
        return None
    
    # Helper: count items in a comma-separated string
    def count_items(val):
        if pd.isna(val) or val.strip() == "":
            return 0
        return len([x for x in val.split(",") if x.strip() != ""])
    
    df = df_raw.copy()
    df["keywords_count"] = df["keywords_matched"].apply(count_items)
    df["semantic_count"] = df["semantic_matches"].apply(count_items)
    df["missing_count"] = df["missing_requirements"].apply(count_items)
    
    # Aggregate per candidate
    df_agg = df.groupby("candidate_email").agg(
        Candidate=("Candidate", "first"),
        KeywordsMatched=("keywords_count", "sum"),
        SemanticMatches=("semantic_count", "sum"),
        MissingRequirements=("missing_count", "sum"),
        MatchPercent=("match_percent", "mean")  # average across categories
    ).reset_index(drop=True)
    
    # Round MatchPercent
    df_agg["MatchPercent"] = df_agg["MatchPercent"].round(2)
    
    return df_agg

import streamlit as st
import pandas as pd
import math

def candidate_match_summary_paginated(df_raw):
    """
    Displays candidate match summary in a paginated, category-wise table.
    Uses actual DB column names: candidate_email, category, keywords_matched, 
    semantic_matches, missing_requirements, match_percent.
    """

    if df_raw.empty:
        st.warning("No candidate match data found.")
        return

    # --- Aggregate per candidate per category ---
    df_grouped = df_raw.groupby(["candidate_email", "category"]).agg({
        "keywords_matched": "sum",
        "semantic_matches": "sum",
        "missing_requirements": "sum",
        "match_percent": "mean"  # average percent across requirements
    }).reset_index()

    # --- Pagination ---
    per_page = 5
    total_records = df_grouped["candidate_email"].nunique()
    total_pages = math.ceil(total_records / per_page)
    
    if "current_page_match" not in st.session_state:
        st.session_state.current_page_match = 1

    start_idx = (st.session_state.current_page_match - 1) * per_page
    end_idx = start_idx + per_page

    # --- Display page header ---
    st.subheader("📊 Candidate Match Summary")

    # --- Display table ---
    display_df = df_grouped[start_idx:end_idx].copy()
    display_df = display_df.rename(columns={
        "candidate_email": "Candidate",
        "category": "Category",
        "keywords_matched": "Keywords Matched",
        "semantic_matches": "Semantic Matches",
        "missing_requirements": "Missing Requirements",
        "match_percent": "Match %"
    })

    # Format Match % nicely
    display_df["Match %"] = display_df["Match %"].round(2)

    st.table(display_df)

    # --- Pagination controls ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.current_page_match > 1:
            if st.button("⬅️ Previous", key="prev_match_page"):
                st.session_state.current_page_match -= 1
                st.experimental_rerun()
    with col3:
        if st.session_state.current_page_match < total_pages:
            if st.button("Next ➡️", key="next_match_page"):
                st.session_state.current_page_match += 1
                st.experimental_rerun()

    st.text(f"Page {st.session_state.current_page_match} of {total_pages}")
    st.text(f"Total Candidates: {total_records}")
