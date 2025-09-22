from collections import Counter
from datetime import datetime
import json
import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.Helper.banner_style import banner_style
from src.database.db_candidates import get_average_score, get_candidates_count, get_candidates_group_by_category, get_candidates_paginated, get_skills_by_category, get_top_candidate, get_total_categories, get_weekly_submissions
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

    col1, col2 = st.columns([2, 2])  # center column wider 

    with col1:
        # Example selected skills
        skills_list = get_skills_by_category(selected_category_id)

        # Optional: show only selected skills
        selected_skills = ["c#", "net", "python", "angular", "javascript"]
        skills_list = [skill for skill in skills_list if skill in selected_skills]

        # Count frequency
        skill_counts = Counter(skills_list)

        if not skill_counts:
            st.warning("No skills found for this category.")
            return

        # Dynamic colors
        def random_color():
            return f'rgb({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)})'

        colors = [random_color() for _ in skill_counts]

        # Plotly bar chart
        fig = go.Figure(
            data=[go.Bar(
                x=list(skill_counts.keys()),
                y=list(skill_counts.values()),
                marker_color=colors
            )]
        )
        fig.update_layout(title_text="Top Selected Skills", xaxis_title="Skill", yaxis_title="Count")

        st.plotly_chart(fig, use_container_width=True)



    
    with col2:
        # ---------------- Weekly Submission Pattern ----------------
        # Aggregate submissions per day

    # Select category

        # Fetch weekly submissions
        weekly_data = get_weekly_submissions(selected_category_id)
        df_weekly = pd.DataFrame(weekly_data)

        # Plot line chart
        fig = px.line(
            df_weekly,
            x="SubmittedOn",
            y="Submissions",
            markers=True,
            title="Weekly Submission Pattern"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Submissions",
            template="plotly_dark"
        )

        st.plotly_chart(fig, use_container_width=True)

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

    # --- Table Header ---
    st.subheader("🏆 Ranked Candidates by Score")
    col_sizes = [1, 3, 3, 2, 2, 2]  # Rank, Candidate, Email, Experience, Score, Action
    columns = st.columns(col_sizes)
    headers = ["Rank", "Candidate", "Email", "Experience", "Score", "Action"]
    for col, header in zip(columns, headers):
        col.markdown(f"**{header}**")

    # --- Table Rows with Inline Expand (clean expander icon) ---
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

    st.text(f"Page {st.session_state.current_page} of {total_pages}")

    # --- Download CSV ---
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Current Page as CSV",
        data=csv,
        file_name=f"resume_analysis_page{st.session_state.current_page}.csv",
        mime="text/csv",
    )
