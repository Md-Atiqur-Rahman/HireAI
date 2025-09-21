import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import streamlit as st
from datetime import datetime

def test_dashboard_page():
    # ---------------- Mock Data ----------------
    # Replace these with your DB calls
    candidates = [
        {"Candidate": "Maria Akter", "Email": "maria@example.com", "Experience": 4, "TotalScore": 90, "Category": "DotNet Developer", "SummaryText": "Excellent .NET skills.",  "Skills": "C#,Python, MongoDb","SubmittedOn": "2025-09-01"},
        {"Candidate": "John Doe", "Email": "john@example.com", "Experience": 5, "TotalScore": 75, "Category": "DotNet Developer", "SummaryText": "Strong C# background.", "Skills": "Python, Sqllite,MongoDb", "SubmittedOn": "2025-09-08"},
        {"Candidate": "Jane Smith", "Email": "jane@example.com", "Experience": 3, "TotalScore": 85, "Category": "React Developer", "SummaryText": "Front-end specialist.", "Skills": "Python, Sqllite,MongoDb","SubmittedOn": "2025-09-08"},
        {"Candidate": "Kumar Raj", "Email": "kumar@example.com", "Experience": 6, "TotalScore": 60, "Category": "DotNet Developer", "SummaryText": "Intermediate skills.", "Skills": "Python, Sqllite,MongoDb","SubmittedOn": "2025-09-08"},
        {"Candidate": "Ali Khan", "Email": "ali@example.com", "Experience": 2, "TotalScore": 95, "Category": "React Developer", "SummaryText": "Excellent React skills.", "Skills": "C#, JavaScript, MongoDb","SubmittedOn": "2025-09-16"},
    ]
    all_skills = []
    df = pd.DataFrame(candidates)
    df['SubmittedOn'] = pd.to_datetime(df['SubmittedOn'])
    # ---------------- Dashboard ----------------
    # st.title("📊 Resume Analysis Dashboard (HireAI)")


# Example: Dynamic last updated timestamp
    last_updated = datetime.now().strftime("%B %d, %Y %I:%M %p")

    st.markdown(f"""
    <style>
    .header-banner {{
        background-color: #2e3b70;  /* dark blue background */
        border-radius: 15px;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #7fd3c7;
        margin-bottom: 20px;
    }}

    .header-left {{
        display: flex;
        align-items: center;
    }}

    .header-left img {{
        width: 50px;
        height: 50px;
        margin-right: 15px;
        border-radius: 10px;
    }}

    .header-title {{
        font-size: 28px;
        font-weight: 600;
    }}
    .header-timestamp {{
        font-size: 14px;
        color: #cce0e0;
    }}
    </style>

    <div class="header-banner">
        <div class="header-left">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135714.png" alt="icon">
            <div class="header-title">Resume Analytics Dashboard</div>
        </div>
        <div class="header-timestamp">Last updated: {last_updated}</div>
    </div>
    """, unsafe_allow_html=True)


    # --- KPI Cards ---
    total_resumes = len(df)
    avg_score = df["TotalScore"].mean()
    top_candidate = df.loc[df["TotalScore"].idxmax()]["Candidate"]
    total_categories = df["Category"].nunique()

    # --- KPI Cards with Border ---
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
            <div class="kpi-value">{total_resumes}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Average Score</div>
            <div class="kpi-value">{avg_score:.1f}%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Top Candidate</div>
            <div class="kpi-value">{top_candidate}</div>
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
        st.subheader("📂 Candidates per Job Category")
        category_counts = df["Category"].value_counts()
        fig_cat = px.pie(names=category_counts.index, values=category_counts.values, title="Resumes per Category")
        st.plotly_chart(fig_cat, use_container_width=True)
    with col2:
            # --- Top Candidates Bar Chart ---
        st.subheader("🏆 Top Candidates by Score")
        top_df = df.sort_values(by="TotalScore", ascending=False)
        fig_top = px.bar(top_df, x="Candidate", y="TotalScore", color="TotalScore", title="Top Candidates")
        st.plotly_chart(fig_top, use_container_width=True)

    col1, col2 = st.columns([2, 2])  # center column wider 
    with col1:
        # --- Candidate Score Distribution ---
        st.subheader("📈 Candidate Score Distribution")
        fig_score = px.histogram(df, x="TotalScore", nbins=10, title="Score Distribution")
        st.plotly_chart(fig_score, use_container_width=True)
    with col2:
        # --- Experience vs Score Scatter ---
        st.subheader("📊 Experience vs Score")
        fig_exp = px.scatter(df, x="Experience", y="TotalScore", color="Category", hover_data=["Candidate"])
        st.plotly_chart(fig_exp, use_container_width=True)
    
    col1, col2 = st.columns([2, 2])  # center column wider 
    with col1:
        for candidate in candidates:
            skills = [skill.strip() for skill in candidate["Skills"].split(",")]
            all_skills.extend(skills)

        # Count frequency
        skill_counts = Counter(all_skills)

        # Generate a color for each skill dynamically
        def random_color():
            return f'rgb({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)})'

        colors = [random_color() for _ in skill_counts]

        # Create Bar chart
        fig_skills = go.Figure(
            data=[go.Bar(
                x=list(skill_counts.keys()), 
                y=list(skill_counts.values()), 
                marker_color=colors  # Dynamic colors applied
            )]
        )

        fig_skills.update_layout(title_text="Top Skills Mentioned in Resumes")
        st.plotly_chart(fig_skills, use_container_width=True)

    
    with col2:
        # ---------------- Weekly Submission Pattern ----------------
        # Aggregate submissions per day
        weekly_df = df.groupby('SubmittedOn').size().reset_index(name='Submissions')

        # Plot line chart
        fig = px.line(
            weekly_df, 
            x='SubmittedOn', 
            y='Submissions', 
            markers=True,  # Show points
            title='Weekly Submission Pattern'
        )

        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Number of Submissions',
            template='plotly_dark'  # For dark theme like your image
        )

        st.plotly_chart(fig, use_container_width=True)

    # --- Candidate Table with Expand/Collapse ---
    st.subheader("🗂 Candidate Details")
    col_sizes = [1, 3, 3, 2, 2, 2]  # Rank, Name, Email, Experience, Score, Action
    columns = st.columns(col_sizes)
    headers = ["Rank", "Candidate", "Email", "Experience", "Score", "Action"]
    for col, header in zip(columns, headers):
        col.markdown(f"**{header}**")

    for idx, row in df.iterrows():
        cols = st.columns(col_sizes)
        cols[0].write(idx + 1)
        cols[1].write(row["Candidate"])
        cols[2].write(row["Email"])
        cols[3].write(f"{row['Experience']} yrs")
        cols[4].write(f"{row['TotalScore']} %")
        
        with cols[5]:
            if st.button("🔍 View", key=f"view_{idx}"):
                with st.expander(f"📄 Analysis for {row['Candidate']}", expanded=True):
                    st.write(f"**Name:** {row['Candidate']}")
                    st.write(f"**Score (%):** {row['TotalScore']}")
                    st.write(f"**Experience:** {row['Experience']}")
                    st.text(row["SummaryText"])

   


    # --- Download All Results ---
    st.subheader("📥 Download Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv,
        file_name="resume_analysis.csv",
        mime="text/csv",
    )
