from src.Helper import banner_style
from src.database.db_job_category import get_all_categories
from src.database.db_candidates import save_candidate
from src.feature.helper_requirement_analyzer.requirement_analysis import evaluate_resume
from src.database.db_job_requirements import get_requirements_by_category
# from src.Helper.resume_feedback import generate_resume_feedback_gemini
import streamlit as st
import pandas as pd
import nltk

import plotly.express as px

from src.Helper.extract_general_info import extract_email, extract_name_from_text, extract_phone
from src.Helper.extractor import extract_keywords
from src.Helper.parser import extract_text_from_pdf
from src.Helper.banner_style import banner_style

def collpase_all_expander():
    for key in ["detailed_analysis_expander"]:
        st.session_state[key] = False
def reset():
    for key in ["results", "analysis_done", "jd_text", "jd_keywords", "resume_files", "analyze_triggered"]:
            st.session_state[key] = [] if "results" in key or key == "jd_keywords" else False if "done" in key or "triggered" in key else ""
    st.rerun()

def multiple_resume_analysis():
        # Download NLTK data
    nltk.download('punkt')      # type: ignore
    nltk.download('stopwords')  # type: ignore
    st.session_state.selected_candidate = None
    collpase_all_expander()

    # Initialize session state
    for key in ["results", "analysis_done", "jd_text", "jd_keywords", "resume_files", "jd_file", "resume_files_input", "analyze_triggered","selected_candidate" ]:
        if key not in st.session_state:
            st.session_state[key] = [] if "results" in key or key == "jd_keywords" else False if "done" in key or "triggered" in key else ""

    # 🔄 Reset button
    if st.button("🔄 Reset App"):
        reset()
    
    

    # UI
    # st.title("📄Multiple Resume Analyzer (HireAI)")
    banner_style("Multiple Resume Analyzer 🔍")
    # Get categories and selected category
    # categories = get_categories()
    # selected_category = st.selectbox("Select Job Requirement Category", ["All"] + categories)
    categories = get_all_categories()  # [(id, name), ...]
    jd_file_input =[]
    if not categories:
        st.warning("No categories found. Please add a category first.")
    else:
        category_dict = {cat['name']: cat['id'] for cat in categories} 

    # Dropdown shows only names
        selected_category_name = st.selectbox("Select Job Category", list(category_dict.keys()))

    # Get corresponding ID
        selected_category_id = category_dict[selected_category_name]
    # Get requirements for that category
        jd_file_input = get_requirements_by_category(selected_category_id)

    
    # jd_file_input = st.file_uploader("Upload Job Description (TXT)", type=["txt"])
    # resume_files_input = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)
    resume_files_input = st.file_uploader(
            "Upload resumes (PDF or TXT)",
            type=["pdf", "txt"],
            accept_multiple_files=True
        )
    # Store uploaded files in session state
    if jd_file_input:
        st.session_state.jd_file = jd_file_input
        # Combine all requirements into a single JD text
        st.session_state.jd_text = "\n".join(jd_file_input)
    if resume_files_input:
        st.session_state.resume_files_input = resume_files_input

    # ✅ Always show Analyze button at top if files are uploaded
    if st.session_state.jd_text  and st.session_state.resume_files_input:
        st.markdown("### 🔍 Ready to Analyze Resumes")
        if st.button("🔍 Analyze Resumes"):
            if not resume_files_input:
                st.warning("Please upload at least one resume file.")
                return
            st.session_state.analyze_triggered = True
            st.session_state.analysis_done = False
    # Layout placeholders
    progress_bar = st.empty()
    status_text = st.empty()
    chart_placeholder = st.empty()
    rank_placeholder = st.empty()
    resume_analysis_container = st.container()



    # ✅ Run analysis only when triggered
    if st.session_state.analyze_triggered and not st.session_state.analysis_done:
        # st.session_state.jd_text = st.session_state.jd_file.read().decode("utf-8")
        st.session_state.jd_keywords = extract_keywords(st.session_state.jd_text)
        st.session_state.resume_files = st.session_state.resume_files_input
        st.session_state.results = []

        total_resumes = len(st.session_state.resume_files)
        progress_bar.progress(0)

        for idx, resume_file in enumerate(st.session_state.resume_files):
            status_text.text(f"🔍 Analyzing: {resume_file.name} ({idx}/{total_resumes})")

            if resume_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(resume_file)
            else:  # txt file
                resume_text = str(resume_file.read(), "utf-8")
            email = extract_email(resume_text)
            phone = extract_phone(resume_text)
            name =extract_name_from_text(resume_text,email)
            summary_text, total_exp, total_score,technicalskills = evaluate_resume(resume_text, st.session_state.jd_file)
            print("skills---->",technicalskills)
            experience = total_exp
            total_score = total_score
            result = {
                "Candidate": name,
                "Email": email,
                "Contact": phone,
                "Experience": experience,
                "TotalScore": total_score,
                "Skills": technicalskills,
                "SummaryText":summary_text
            }

            save_candidate(name, email, phone, experience, total_score, technicalskills, summary_text, selected_category_id)


            st.session_state.results.append(result)

            df_so_far = pd.DataFrame(st.session_state.results).sort_values(by="TotalScore", ascending=False).reset_index(drop=True)
            df_so_far.index += 1
            df_so_far.index.name = "Rank"

            with chart_placeholder.container():
                st.subheader("📊 Score Comparison")
                fig = px.bar(df_so_far, x="Candidate", y="TotalScore", color="Candidate", title="Score per Candidate")
                st.plotly_chart(fig, key=f"realtime_chart_{idx}")
                
                

            with rank_placeholder.container():
                st.subheader("🏆 Ranked Candidates by Score")
                
                # Table headers
                header_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
                header_cols[0].markdown("**Rank**")
                header_cols[1].markdown("**Candidate**")
                header_cols[2].markdown("**Email**")
                header_cols[3].markdown("**Contact**")
                header_cols[4].markdown("**Experience**")
                header_cols[5].markdown("**TotalScore**")
                header_cols[6].markdown("**Action**")

                # Table rows
                for i, row in df_so_far.iterrows():
                    row_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
                    row_cols[0].markdown(f"{i}")
                    row_cols[1].markdown(row["Candidate"])
                    row_cols[2].markdown(row["Email"])
                    row_cols[3].markdown(row["Contact"])
                    row_cols[4].markdown(row["Experience"])
                    row_cols[5].markdown(row["TotalScore"])
                    # unique_id = f"{row['Email']}_{idx}"
                    unique_id = f"{row['Email']}_{i}_{idx}"
                    if row_cols[6].button("Details", key=f"details_btn_live_{unique_id}"):
                        st.session_state.selected_candidate = row.to_dict()
                        st.session_state["detailed_analysis_expander"] = True


            progress_bar.progress((idx + 1) / total_resumes)

        status_text.text("✅ All resumes analyzed successfully!")
        st.session_state.analysis_done = True

    # ✅ Re-render everything if analysis is done
    if st.session_state.analysis_done and st.session_state.results:
        
        # Initialize session state for selected candidate
        if "selected_candidate" not in st.session_state:
            st.session_state.selected_candidate = None

        df_final = pd.DataFrame(st.session_state.results).sort_values(by="TotalScore", ascending=False).reset_index(drop=True)
        df_final.index += 1
        df_final.index.name = "Rank"

        with chart_placeholder.container():
            st.subheader("📊 Score Comparison")
            fig = px.bar(df_final, x="Candidate", y="TotalScore", color="Candidate", title="Score per Candidate")
            st.plotly_chart(fig, key="final_chart")

        with rank_placeholder.container():
            st.subheader("🏆 Ranked Candidates by Score")
            
        # Table headers
            header_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
            header_cols[0].markdown("**Rank**")
            header_cols[1].markdown("**Candidate**")
            header_cols[2].markdown("**Email**")
            header_cols[3].markdown("**Contact**")
            header_cols[4].markdown("**Experience**")
            header_cols[5].markdown("**TotalScore**")
            header_cols[6].markdown("**Action**")

            # Table rows
            for i, row in df_final.iterrows():
                row_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
                row_cols[0].markdown(f"{i}")
                row_cols[1].markdown(row["Candidate"])
                row_cols[2].markdown(row["Email"])
                row_cols[3].markdown(row["Contact"])
                row_cols[4].markdown(row["Experience"])
                row_cols[5].markdown(row["TotalScore"])
                unique_id = f"{row['Email']}_{i}_{row.name}"
                if row_cols[6].button("Details", key=f"details_btn_final_{unique_id}"):
                    st.session_state.selected_candidate = row.to_dict()
                    st.session_state["detailed_analysis_expander"] = True


            csv = df_final.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download All Results as CSV",
                data=csv,
                file_name="resume_analysis_results.csv",
                mime="text/csv",
                key="download_rank_table"
            )

    # 📄 Detailed Section (Toggleable)
    if st.session_state.selected_candidate is not None:
        candidate = st.session_state.selected_candidate

        # If it's a Series, convert to dict
        if isinstance(candidate, pd.Series):
            candidate = candidate.to_dict()
            st.session_state.selected_candidate = candidate
        if not isinstance(candidate, dict):
            candidate = {"Candidate": str(candidate)}

        # Use .get() to avoid KeyError
        candidate_name = candidate.get("Candidate", "Unknown Candidate")
        candidate_score = candidate.get("TotalScore", 0)
        candidate_summary = candidate.get("SummaryText", "")

        with resume_analysis_container.container():
            st.subheader(f"📄 Analysis for {candidate_name}")
            with st.expander("📋 Detailed Analysis", expanded=st.session_state.get("detailed_analysis_expander", False)):
                st.session_state["detailed_analysis_expander"] = True 
                st.write(f"**Score (%):** {candidate_score}")
                st.text(candidate_summary)

            if st.button("❌ Close Details"):
                st.session_state.selected_candidate = None
                st.session_state["detailed_analysis_expander"] = False  # reset expander state

