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
        {"Candidate": "Maria Akter", "Email": "maria@example.com", "Experience": 4, "TotalScore": 90, "Category": "DotNet Developer", "SummaryText": "Excellent .NET skills."},
        {"Candidate": "John Doe", "Email": "john@example.com", "Experience": 5, "TotalScore": 75, "Category": "DotNet Developer", "SummaryText": "Strong C# background."},
        {"Candidate": "Jane Smith", "Email": "jane@example.com", "Experience": 3, "TotalScore": 85, "Category": "React Developer", "SummaryText": "Front-end specialist."},
        {"Candidate": "Kumar Raj", "Email": "kumar@example.com", "Experience": 6, "TotalScore": 60, "Category": "DotNet Developer", "SummaryText": "Intermediate skills."},
        {"Candidate": "Ali Khan", "Email": "ali@example.com", "Experience": 2, "TotalScore": 95, "Category": "React Developer", "SummaryText": "Excellent React skills."},
    ]

    df = pd.DataFrame(candidates)

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
    st.subheader("🔑 Key Metrics")
    total_resumes = len(df)
    avg_score = df["TotalScore"].mean()
    top_candidate = df.loc[df["TotalScore"].idxmax()]["Candidate"]
    total_categories = df["Category"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Resumes", total_resumes)
    col2.metric("Average Score", f"{avg_score:.1f}%")
    col3.metric("Top Candidate", top_candidate)
    col4.metric("Job Categories", total_categories)

    # --- Candidate Score Distribution ---
    st.subheader("📈 Candidate Score Distribution")
    fig_score = px.histogram(df, x="TotalScore", nbins=10, title="Score Distribution")
    st.plotly_chart(fig_score, use_container_width=True)

    # --- Experience vs Score Scatter ---
    st.subheader("📊 Experience vs Score")
    fig_exp = px.scatter(df, x="Experience", y="TotalScore", color="Category", hover_data=["Candidate"])
    st.plotly_chart(fig_exp, use_container_width=True)

    # --- Candidates per Category ---
    st.subheader("📂 Candidates per Job Category")
    category_counts = df["Category"].value_counts()
    fig_cat = px.pie(names=category_counts.index, values=category_counts.values, title="Resumes per Category")
    st.plotly_chart(fig_cat, use_container_width=True)

    # --- Top Candidates Bar Chart ---
    st.subheader("🏆 Top Candidates by Score")
    top_df = df.sort_values(by="TotalScore", ascending=False)
    fig_top = px.bar(top_df, x="Candidate", y="TotalScore", color="TotalScore", title="Top Candidates")
    st.plotly_chart(fig_top, use_container_width=True)

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

    # --- Skills / Keywords Cloud ---
    st.subheader("🛠 Skills / Keywords (Mock)")
    # Mock skill extraction
    skills_list = ["Python", "C#", ".NET", "React", "JavaScript", "SQL", "Django", "Flask"]
    skill_counts = Counter(skills_list)
    fig_skills = go.Figure(data=[go.Bar(x=list(skill_counts.keys()), y=list(skill_counts.values()), marker_color='green')])
    fig_skills.update_layout(title_text="Top Skills Mentioned in Resumes")
    st.plotly_chart(fig_skills, use_container_width=True)

    # --- Download All Results ---
    st.subheader("📥 Download Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        data=csv,
        file_name="resume_analysis.csv",
        mime="text/csv",
    )
