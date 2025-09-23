from src.feature.dashboards.charts.top_skills_chart import top_selected_skills_chart
from src.feature.dashboards.charts.weekly_submission_chart import weekly_submissions_chart
import streamlit as st

def weeklysubmission_topskills_charts(selected_category_id):
    col1, col2 = st.columns([2, 2])  # center column wider 
    with col1:
        # Example selected skills
        top_selected_skills_chart(selected_category_id)
    with col2:
        # ---------------- Weekly Submission Pattern ----------------
       weekly_submissions_chart(selected_category_id) 