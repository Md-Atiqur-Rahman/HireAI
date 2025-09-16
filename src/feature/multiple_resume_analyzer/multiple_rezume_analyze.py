from src.Helper.ats_score import calculate_ats_score
# from src.Helper.resume_feedback import generate_resume_feedback_gemini
import streamlit as st
import pandas as pd
import nltk

from sklearn.feature_extraction.text import TfidfVectorizer
import plotly.express as px

from src.Helper.extract_experience_details import extract_experience_entries
from src.Helper.extract_general_info import extract_email, extract_entities, extract_phone, filter_organizations
from src.Helper.extract_skills import extract_skills_tfidf
from src.Helper.semantic_similarity import calculate_semantic_similarity
from src.Helper.extractor import extract_keywords
from src.Helper.parser import extract_text_from_pdf


def multiple_resume_analysis():
    # Download NLTK data
    nltk.download('punkt')
    nltk.download('stopwords')

    # Initialize session state
    for key in ["results", "analysis_done", "jd_text", "jd_keywords", "resume_files", "jd_file", "resume_files_input", "analyze_triggered"]:
        if key not in st.session_state:
            st.session_state[key] = [] if "files" in key or key == "jd_keywords" else False if "done" in key or "triggered" in key else ""

    # 🔄 Reset button
    if st.button("🔄 Reset App"):
        for key in ["results", "analysis_done", "jd_text", "jd_keywords", "resume_files", "analyze_triggered"]:
            st.session_state[key] = [] if "results" in key or key == "jd_keywords" else False if "done" in key or "triggered" in key else ""
        st.rerun()

    # UI
    st.title("📄 Resume Analyzer (HireAI)")

    jd_file_input = st.file_uploader("Upload Job Description (TXT)", type=["txt"])
    resume_files_input = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

    # Store uploaded files in session state
    if jd_file_input:
        st.session_state.jd_file = jd_file_input
    if resume_files_input:
        st.session_state.resume_files_input = resume_files_input

    # ✅ Always show Analyze button at top if files are uploaded
    if st.session_state.jd_file and st.session_state.resume_files_input:
        st.markdown("### 🔍 Ready to Analyze Resumes")
        if st.button("🔍 Analyze Resumes"):
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
        st.session_state.jd_text = st.session_state.jd_file.read().decode("utf-8")
        st.session_state.jd_keywords = extract_keywords(st.session_state.jd_text)
        st.session_state.resume_files = st.session_state.resume_files_input
        st.session_state.results = []

        total_resumes = len(st.session_state.resume_files)
        progress_bar.progress(0)

        for idx, resume_file in enumerate(st.session_state.resume_files):
            status_text.text(f"🔍 Analyzing: {resume_file.name} ({idx}/{total_resumes})")

            resume_text = extract_text_from_pdf(resume_file)
            resume_keywords = extract_keywords(resume_text)
            email = extract_email(resume_text)
            phone = extract_phone(resume_text)
            #experience = extract_experience_duration(resume_text)
            experience_details, experience  = extract_experience_entries(resume_text)
            orgInfo =extract_entities(resume_text)
            skills = extract_skills_tfidf(resume_text,st.session_state.jd_text)
            documents = [st.session_state.jd_text, resume_text]
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()
            jd_scores = tfidf_matrix[0].toarray()[0]
            resume_scores = tfidf_matrix[1].toarray()[0]

            tfidf_match_score = sum([jd_scores[i] for i in range(len(feature_names)) if jd_scores[i] > 0.1 and resume_scores[i] > 0]) / sum(jd_scores) * 100 if sum(jd_scores) > 0 else 0
            semantic_similarity_score = calculate_semantic_similarity(resume_text, st.session_state.jd_text)
            keyword_coverage_score = len(set(resume_keywords).intersection(set(st.session_state.jd_keywords))) / len(set(st.session_state.jd_keywords)) * 100 if st.session_state.jd_keywords else 0
            fit_score = (0.4 * tfidf_match_score) + (0.4 * semantic_similarity_score) + (0.2 * keyword_coverage_score)

            missing_keywords = [word for i, word in enumerate(feature_names) if jd_scores[i] > 0.1 and resume_scores[i] == 0]
            generic_terms = {"also", "us", "x", "join", "apply", "offer", "required", "preferred", "related", "within", "looking", "invite"}
            missing_keywords = [kw for kw in missing_keywords if kw not in generic_terms]
            orgs_raw = orgInfo.get("Organizations", [])
            orgs_filtered = filter_organizations(orgs_raw, resume_text)
            ats_result = calculate_ats_score(resume_text, st.session_state.jd_text)
            # feedback = generate_resume_feedback_gemini(resume_text, st.session_state.jd_text)
            # result["Feedback"] = feedback

            result = {
                "Candidate": orgInfo["Name"],
                "Email": email,
                "Contact": phone,
                "Organizations":orgs_filtered,
                "Designations": orgInfo.get("Designations", []),
                "Experience": experience,
                "ExperienceDetails": experience_details,
                "ATS Score": ats_result["ATS Score"],
                "Keyword Match Score (%)":ats_result["Keyword Match Score (%)"],
                "Matched Keywords":ats_result["Matched Keywords"],
                "Missing Keywords":ats_result["Missing Keywords"],
                "Formatting Deductions":ats_result["Formatting Deductions"],

                "TF-IDF Match (%)": round(tfidf_match_score, 2),
                "Semantic Similarity (%)": round(semantic_similarity_score, 2),
                "Keyword Coverage (%)": round(keyword_coverage_score, 2),
                "Fit Score (%)": round(fit_score, 2),
                "Missing Keywords": ", ".join(missing_keywords),
                "Skills": skills,
            }

            st.session_state.results.append(result)

            df_so_far = pd.DataFrame(st.session_state.results).sort_values(by="ATS Score", ascending=False).reset_index(drop=True)
            df_so_far.index += 1
            df_so_far.index.name = "Rank"

            with chart_placeholder.container():
                st.subheader("📊 ATS Score Comparison")
                fig = px.bar(df_so_far, x="Candidate", y="ATS Score", color="Candidate", title="ATS Score per Candidate")
                st.plotly_chart(fig, key=f"realtime_chart_{idx}")
                
                

            with rank_placeholder.container():
                st.subheader("🏆 Ranked Candidates by ATS Score")
                
                # Table headers
                header_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
                header_cols[0].markdown("**Rank**")
                header_cols[1].markdown("**Candidate**")
                header_cols[2].markdown("**Email**")
                header_cols[3].markdown("**Contact**")
                header_cols[4].markdown("**Experience**")
                header_cols[5].markdown("**ATS Score**")
                header_cols[6].markdown("**Action**")

                # Table rows
                for i, row in df_so_far.iterrows():
                    row_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
                    row_cols[0].markdown(f"{i}")
                    row_cols[1].markdown(row["Candidate"])
                    row_cols[2].markdown(row["Email"])
                    row_cols[3].markdown(row["Contact"])
                    row_cols[4].markdown(row["Experience"])
                    row_cols[5].markdown(row["ATS Score"])
                    unique_id = f"{row['Email']}_{idx}"
                    if row_cols[6].button("Details", key=f"details_btn_live_{unique_id}"):
                        st.session_state.selected_candidate = row.to_dict()



            progress_bar.progress((idx + 1) / total_resumes)

        status_text.text("✅ All resumes analyzed successfully!")
        st.session_state.analysis_done = True

    # ✅ Re-render everything if analysis is done
    if st.session_state.analysis_done and st.session_state.results:
        
        # Initialize session state for selected candidate
        if "selected_candidate" not in st.session_state:
            st.session_state.selected_candidate = None

        df_final = pd.DataFrame(st.session_state.results).sort_values(by="ATS Score", ascending=False).reset_index(drop=True)
        df_final.index += 1
        df_final.index.name = "Rank"

        with chart_placeholder.container():
            st.subheader("📊 Fit Score Comparison")
            fig = px.bar(df_final, x="Candidate", y="ATS Score", color="Candidate", title="ATS Score per Candidate")
            st.plotly_chart(fig, key="final_chart")

        with rank_placeholder.container():
            st.subheader("🏆 Ranked Candidates by ATS Score")
            
        # Table headers
            header_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
            header_cols[0].markdown("**Rank**")
            header_cols[1].markdown("**Candidate**")
            header_cols[2].markdown("**Email**")
            header_cols[3].markdown("**Contact**")
            header_cols[4].markdown("**Experience**")
            header_cols[5].markdown("**ATS Score**")
            header_cols[6].markdown("**Action**")

            # Table rows
            for i, row in df_final.iterrows():
                row_cols = st.columns([1, 3, 2, 2, 2, 1, 2])
                row_cols[0].markdown(f"{i}")
                row_cols[1].markdown(row["Candidate"])
                row_cols[2].markdown(row["Email"])
                row_cols[3].markdown(row["Contact"])
                row_cols[4].markdown(row["Experience"])
                row_cols[5].markdown(row["ATS Score"])
                unique_id = f"{row['Email']}_{i}"
                if row_cols[6].button("Details", key=f"details_btn_final_{unique_id}"):
                    st.session_state.selected_candidate = row.to_dict()



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
            with resume_analysis_container.container():
                st.subheader(f"📄 Analysis for {candidate.get('Candidate', 'Unknown')}")
                with st.expander("📋 Detailed Analysis", expanded=True):
                    # st.write(f"**ATS Score (%):** {candidate['ATS Score']}")
                    # st.write(f"**Name:** {candidate['Candidate']}")
                    # st.write(f"**Email Address:** {candidate.get('Email', 'Not found')}")
                    # st.write(f"**Contact Number:** {candidate.get('Contact', 'Not found')}")
                    # st.write(f"**Experience:** {candidate.get('Experience', 'Not found')}")
                    # experience_details = candidate.get("ExperienceDetails")
                    # for entry in experience_details:
                    #     st.write(entry)
                    
                    # st.write("**Skills:**", ", ".join(candidate.get("Skills", [])))
                    # st.write("**Matched Keywords:**", ", ".join(candidate.get("Matched Keywords", [])))
                    # Test------------------------
                    # "Keyword Match Score (%)":ats_result["Keyword Match Score (%)"],
                    # "TF-IDF Match (%)": round(tfidf_match_score, 2),
                    # "Semantic Similarity (%)": round(semantic_similarity_score, 2),
                    # "Keyword Coverage (%)": round(keyword_coverage_score, 2),
                    # "Fit Score (%)": round(fit_score, 2),
    # 
                    # "Missing Keywords": ", ".join(missing_keywords),
                    st.write(f"**ATS Keyword Match Score (%):** {candidate['Keyword Match Score (%)']}")
                    st.write(f"**TF-IDF Keyword Match Score (%):** {candidate['TF-IDF Match (%)']}")
                    st.write(f"**Semantic Similarity Keyword Match Score (%):** {candidate['Semantic Similarity (%)']}")
                    st.write(f"**Keyword Coverage Match Score (%):** {candidate['Keyword Coverage (%)']}")
                    st.write(f"**ATS Score (%):** {candidate['ATS Score']}")
                    st.write(f"**Fit Score (%):** {candidate['Fit Score (%)']}")
                    
                if st.button("❌ Close Details"):
                    st.session_state.selected_candidate = None
