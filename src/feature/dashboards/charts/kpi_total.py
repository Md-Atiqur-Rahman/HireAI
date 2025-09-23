
from src.database.db_candidates import get_average_score, get_top_candidate, get_total_categories
import streamlit as st

def kpi_total_card(selected_category_id,total_records):
    # --- KPI Cards with Border ---
    avg_score = get_average_score(selected_category_id)
    top_candidate = get_top_candidate(selected_category_id)
    total_categories = get_total_categories(selected_category_id)

    st.subheader("🔑 Key Metrics")

    kpi_html = f"""
    <style>
    .kpi-container {{
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
    }}
    .kpi-card {{
        flex: 1;
        background-color: #2e3b70;
        border: 2px solid #2e3b70;
        color: #cce0e0;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }}
    .kpi-title {{
        font-size: 18px;
        font-weight: 600;
        color:  #cce0e0;
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 700;
        margin-top: 10px;
        color:  #cce0e0;
    }}
    </style>

    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">Total Resumes</div>
            <div class="kpi-value">{total_records}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Average Score</div>
            <div class="kpi-value">{avg_score:.1f}%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Top Candidate</div>
            <div class="kpi-value">{top_candidate['name']}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Job Categories</div>
            <div class="kpi-value">{total_categories}</div>
        </div>
    </div>
    """

    st.markdown(kpi_html, unsafe_allow_html=True)