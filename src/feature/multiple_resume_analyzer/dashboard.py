import streamlit as st
import pandas as pd
import plotly.express as px

from src.database.db_candidates import get_all_candidates
from src.database.db_job_category import get_all_categories

def dashboard_page():
    st.title("📊 Resume Analysis Dashboard (HireAI)")

    # Fetch categories and prepare filter
    categories = get_all_categories()  # Returns list of dicts [{'id':1, 'name':'Software Engineer'}, ...]
    category_dict = {cat['name']: cat['id'] for cat in categories}

    selected_category_name = st.selectbox("Select Job Category", ["All"] + list(category_dict.keys()))

    # Fetch all candidates from DB
    candidates = get_all_candidates()  # Returns list of dicts with Candidate info
    df = pd.DataFrame(candidates)

    if df.empty:
        st.info("No candidate data found in the database.")
        return

    # Apply category filter
    if selected_category_name != "All":
        selected_category_id = category_dict[selected_category_name]
        df = df[df["CategoryId"] == selected_category_id]

    if df.empty:
        st.warning(f"No candidates found for category '{selected_category_name}'.")
        return

    # Sort by TotalScore descending
    df = df.sort_values(by="TotalScore", ascending=False).reset_index(drop=True)
    df.index += 1
    df.index.name = "Rank"

    # 📊 Score comparison chart
    st.subheader("📊 Score Comparison")
    fig = px.bar(df, x="Candidate", y="TotalScore", color="Candidate", title="Score per Candidate")
    st.plotly_chart(fig)

    # 🏆 Ranked candidates table
    st.subheader("🏆 Ranked Candidates by Score")
    header_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
    header_cols[0].markdown("**Rank**")
    header_cols[1].markdown("**Candidate**")
    header_cols[2].markdown("**Email**")
    header_cols[3].markdown("**Contact**")
    header_cols[4].markdown("**Experience**")
    header_cols[5].markdown("**TotalScore**")
    header_cols[6].markdown("**Action**")

    if "selected_candidate" not in st.session_state:
        st.session_state.selected_candidate = None

    for i, row in df.iterrows():
        row_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
        row_cols[0].markdown(f"{i}")
        row_cols[1].markdown(row["Candidate"])
        row_cols[2].markdown(row["Email"])
        row_cols[3].markdown(row["Contact"])
        row_cols[4].markdown(row["Experience"])
        row_cols[5].markdown(row["TotalScore"])
        unique_id = f"{row['Email']}_{i}"
        if row_cols[6].button("Details", key=f"details_btn_{unique_id}"):
            st.session_state.selected_candidate = row.to_dict()

    # 📄 Detailed candidate analysis
    if st.session_state.selected_candidate:
        candidate = st.session_state.selected_candidate
        with st.expander(f"📄 Analysis for {candidate['Candidate']}", expanded=True):
            st.write(f"**Name:** {candidate['Candidate']}")
            st.write(f"**Score (%):** {candidate['TotalScore']}")
            st.write(f"**Experience:** {candidate['Experience']}")
            st.text(candidate['SummaryText'])
        if st.button("❌ Close Details"):
            st.session_state.selected_candidate = None

    # 📥 Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download All Results as CSV",
        data=csv,
        file_name="resume_analysis_results.csv",
        mime="text/csv",
    )
