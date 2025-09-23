
from src.database.db_candidates import get_weekly_submissions
import pandas as pd
import plotly.express as px
import streamlit as st

def weekly_submissions_chart(selected_category_id):
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