from collections import Counter
from datetime import datetime
import json
import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.feature.helper_requirement_analyzer.table import ranked_candidates_by_Score_table
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
    if "selected_candidate" not in st.session_state:
        st.session_state.selected_candidate = None

    # --- Job Category Filter ---
    categories = get_all_categories()
    category_dict = {cat['name']: cat['id'] for cat in categories}
    selected_category_name = st.selectbox("Select Job Category", ["All"] + list(category_dict.keys()))
    selected_category_id = 0
    if selected_category_name != "All":
        selected_category_id = category_dict[selected_category_name]

    # --- Pagination Setup ---
    # print(selected_category_id)
    per_page = 5
    total_records = get_candidates_count(selected_category_id)
    total_pages = (total_records // per_page) + (1 if total_records % per_page else 0)
    offset = (st.session_state.current_page - 1) * per_page

    candidates = get_candidates_paginated(selected_category_id, per_page, offset)
    if not candidates:
        st.info("No candidate data found.")
        return

    df = pd.DataFrame(candidates)

    # --- Add Rank Column ---
    df["Rank"] = range(offset + 1, offset + len(df) + 1)
    
    ## Chart starts
    # --- Kpi Cards ---
    kpi_total_card(selected_category_id,total_records)
    # --- Candidate by category chart ---
    show_chart_candidate_by_category(df,selected_category_id)
     # ---------------- Weekly Submission and Topskills charts ----------------
    weeklysubmission_topskills_charts(selected_category_id)
    # ------------------ Candidate Score Distribution ---
    candidate_score_vs_experience(df)
    # ------------------ Table----------------------------
    ranked_candidates_by_Score_table(df,total_records)
  


    
