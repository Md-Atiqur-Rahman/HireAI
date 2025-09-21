import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.db_candidates import get_candidates_count, get_candidates_paginated
from src.database.db_job_category import get_all_categories

def dashboard_page():
    st.title("📊 Resume Analysis Dashboard (HireAI)")

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
    
    # Create 3 columns: left empty, center for chart, right empty
    col1, col2, col3 = st.columns([1, 2, 1])  # center column wider

    with col2:
        st.subheader("📈 Total Resumes Analyzed")
        
        fig_total = px.pie(
            names=["Resumes Analyzed"], 
            values=[total_records], 
            hole=0.4,  # Bigger hole = smaller circle
        )

        # Hide text labels on slices
        fig_total.update_traces(
            textinfo='none', 
            marker_colors=['#636EFA']  # Optional color
        )

        # Add bold annotation in the middle
        fig_total.update_layout(
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            width=300,  # Smaller width
            height=300,  # Smaller height
            annotations=[dict(
                text=f"<b>{total_records}</b>",  # Bold
                x=0.5, y=0.5,  # Center
                font=dict(size=30, color="black"),
                showarrow=False
            )]
        )

        st.plotly_chart(fig_total, use_container_width=False)

    # --- Score Comparison Chart ---
    st.subheader("📊 Score Comparison")
    fig = px.bar(df, x="Candidate", y="TotalScore", color="Candidate", title="Score per Candidate")
    st.plotly_chart(fig)

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

  
    # --- Pagination Controls ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous") and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
            st.rerun()
    with col3:
        if st.button("Next ➡️") and st.session_state.current_page < total_pages:
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
