from collections import Counter
import random
import streamlit as st
import plotly.graph_objects as go

from src.database.db_candidates import get_skills_by_category

def top_selected_skills_chart(selected_category_id):
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