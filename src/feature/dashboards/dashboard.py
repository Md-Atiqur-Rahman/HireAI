from collections import Counter
from datetime import datetime
import json
import math
import os
import random
import sys
from numpy import ceil
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from src.database.db_keyword_match_analysis import candidate_match_summary_aggregated, candidate_match_summary_table, get_raw_candidate_data
from src.feature.helper_requirement_analyzer.ranked_candidate_table import ranked_candidates_by_Score_table
from src.database.db_keyword_match_analysis import candidate_match_summary_aggregated, candidate_match_summary_table, get_raw_candidate_data
from src.feature.helper_requirement_analyzer.table import candidate_scores_table
from src.feature.dashboards.charts.candidate_score_experience_chart import candidate_score_vs_experience
from src.feature.dashboards.charts.weekly_submission_to_skillis_chart import weeklysubmission_topskills_charts
from src.feature.dashboards.charts.candidate_category_chart import show_chart_candidate_by_category
from src.feature.dashboards.charts.kpi_total import kpi_total_card
from src.Helper.banner_style import banner_style
from src.database.db_candidates import  get_candidates_count, get_candidates_paginated
from src.database.db_job_category import get_all_categories

def dashboard_page():
    # st.title("📊 Resume Analysis Dashboard (HireAI)")
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")
    banner_style("Resume Analytics Dashboard", last_updated)
    # --- Session State Initialization ---
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    # if "selected_candidate" not in st.session_state:
    #     st.session_state.selected_candidate = None
    # --- Session State Initialization for pagination ---
    if "page_match_summary" not in st.session_state:
        st.session_state.page_match_summary = 1
    if "page_scores_summary" not in st.session_state:
        st.session_state.page_scores_summary = 1
    if "page_ranked_candidates" not in st.session_state:
        st.session_state.page_ranked_candidates = 1

    per_page = 5

    # --- Job Category Filter ---
    categories = get_all_categories()
    category_dict = {cat['name']: cat['id'] for cat in categories}
    # আগের category রাখো
    if "prev_category" not in st.session_state:
        st.session_state.prev_category = "All"

    selected_category_name = st.selectbox("Select Job Category", ["All"] + list(category_dict.keys()))
    selected_category_id = 0
    if selected_category_name != "All":
        selected_category_id = category_dict[selected_category_name]

    # ✅ category change হলে pagination reset করো
    if selected_category_name != st.session_state.prev_category:
        st.session_state.page_match_summary = 1
        st.session_state.page_scores_summary = 1
        st.session_state.page_ranked_candidates = 1
        st.session_state.current_page = 1
        st.session_state.prev_category = selected_category_name
        # --- Pagination Setup ---
    per_page = 5

    # ----- Candidate Scores & Ranked Candidates -----
    total_records = get_candidates_count(selected_category_id)
    total_pages_scores = ceil(total_records / per_page)
    offset_scores = (st.session_state.current_page - 1) * per_page
    df_candidates = pd.DataFrame(get_candidates_paginated(selected_category_id, per_page, offset_scores))
    count_rows = len(df_candidates)
    df_candidates["Rank"] = range(offset_scores + 1, offset_scores + len(df_candidates) + 1)
    count_rows = len(df_candidates)
    if df_candidates.empty:
        st.info("No candidate data found.")
        return

    #--- KPI Cards ---
    kpi_total_card(selected_category_id, total_records)

    # ----- Ranked Candidate Overview Table -----

    
    df_rank_table = ranked_candidates_by_Score_table(selected_category_id,per_page, total_records,total_pages_scores)
    st.session_state.df_rank_table = df_rank_table


    #----- Candidate Keyword Match Analysis  -----
    df_raw = get_raw_candidate_data()
    if df_raw is not None and not df_raw.empty:
        df_aggregated = candidate_match_summary_aggregated(df_raw)
        if df_aggregated is not None and not df_aggregated.empty:
            
            candidate_match_summary_table(df_aggregated,per_page)
            #df_candidates = df_match_paginated
            

    # ----- Candidate Scores Summary -----
    df_candidates_Scores = candidate_scores_table(selected_category_id, per_page, total_records,total_pages_scores)
    st.session_state.df_candidates_Scores = df_candidates_Scores
    

    # Detect which table’s page changed and set it as active
    if st.session_state.page_ranked_candidates != st.session_state.get("prev_page_ranked", 0):
        st.session_state.last_table = "rank"
    # if st.session_state.page_match_summary != st.session_state.get("prev_page_match", 0):
    #     st.session_state.last_table = "match"
    if st.session_state.page_scores_summary != st.session_state.get("prev_page_scores", 0):
        st.session_state.last_table = "scores"

    # Update previous page trackers
    st.session_state.prev_page_ranked = st.session_state.page_ranked_candidates
    #st.session_state.prev_page_match = st.session_state.page_match_summary
    st.session_state.prev_page_scores = st.session_state.page_scores_summary

    # Default (if nothing selected yet)
    if "last_table" not in st.session_state:
        st.session_state.last_table = "rank"

    # Choose df_candidates dynamically
    if st.session_state.last_table == "rank":
        df_candidates = st.session_state.df_rank_table
    elif st.session_state.last_table == "scores":
        df_candidates = st.session_state.df_candidates_Scores
        


    #----- Charts -----
    # st.write("🧾 df_candidates info:")
    # st.write("Shape:", df_candidates.shape)
    # st.write("Columns:", df_candidates.columns.tolist())
    # st.dataframe(df_candidates.head())
    show_chart_candidate_by_category(df_candidates, selected_category_id)
    weeklysubmission_topskills_charts(selected_category_id)
    candidate_score_vs_experience(df_candidates)


    
    
    
