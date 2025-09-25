# import streamlit as st
# from src.feature.home import home_page
# from src.Admin.job_requirment import job_requirements_page
# from src.feature.dashboards.dashboard import dashboard_page
# from src.feature.multiple_resume_analyzer.multiple_rezume_analyze import multiple_resume_analysis
# from src.feature.resume_analyzer.single_resume_analyzer import resume_uploader
# from src.Admin.job_category_page import job_category_page

# import sys, os
# sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# st.set_page_config(page_title="Hire AI", page_icon="https://cdn-icons-png.flaticon.com/512/3135/3135714.png", layout="wide")

# # Initialize session state
# if "page" not in st.session_state:
#     st.session_state.page = "home"

# # Sidebar CSS
# st.markdown("""
# <style>
# [data-testid="stSidebar"] {
#     background-color: #1e1e2f;
#     padding: 20px 10px;
# }
# .sidebar-logo {text-align:center;margin-bottom:20px;}
# .sidebar-title {font-size:22px;font-weight:bold;text-align:center;color:#5dade2;margin-bottom:25px;}

# /* Make all buttons same size */
# [data-testid="stSidebar"] .stButton>button {
#     width: 200px !important; /* fixed width */
#     height: 50px !important; /* fixed height */
#     margin: 8px 0 !important;
#     border-radius: 12px !important;
#     font-size: 16px !important;
#     font-weight: 600 !important;
#     text-align: left;
#     color: white !important;
#     background: linear-gradient(90deg, #3498db, #5dade2) !important;
#     border: none !important;
#     transition: 0.3s !important;
# }
# [data-testid="stSidebar"] .stButton>button:hover {
#     background: linear-gradient(90deg, #1abc9c, #16a085) !important;
# }
# </style>
# """, unsafe_allow_html=True)

# # Sidebar menu
# with st.sidebar:
#     st.markdown('<div class="sidebar-logo"><img src="https://cdn-icons-png.flaticon.com/512/3135/3135714.png" width="120"></div>', unsafe_allow_html=True)
#     st.markdown('<div class="sidebar-title">Hire AI</div>', unsafe_allow_html=True)

#     menu_items = {
#     "🏠 Home": "home",                        # Home page
#     "📄 Resume Analyzer": "analyzer",         # Analyze a single resume
#     "🔍 All Resumes Analyzer": "allanalyzer", # Analyze multiple resumes
#     "📊 Dashboard": "dashboard",              # Dashboard overview
#     "📝 Add Requirements": "JobRequirements", # Add new job requirements
#     "📂 Add Categories": "JobCategories"      # Add new job categories
# }

#     for label, page_name in menu_items.items():
#         btn_key = f"btn_{page_name}"
#         clicked = st.button(label, key=btn_key)
#         if clicked:
#             st.session_state.page = page_name

# # Page routing
# page = st.session_state.page
# if page == "home":
#     home_page()
# elif page == "analyzer":
#     resume_uploader()
# elif page == "allanalyzer":
#     multiple_resume_analysis()
# elif page == "dashboard":
#     dashboard_page()
# elif page == "JobRequirements":
#     job_requirements_page()
# elif page == "JobCategories":
#     job_category_page()


# # add_submitted_on_column()
# # update_submitted_on(10, "2025-08-03")

# # update_submitted_on(11, "2025-08-10")
# # update_submitted_on(12, "2025-08-10")

# # update_submitted_on(13, "2025-08-17")
# # update_submitted_on(14, "2025-08-17")
# # update_submitted_on(15, "2025-08-17")

# # update_submitted_on(16, "2025-08-24")
# # update_submitted_on(17, "2025-08-24")
# # update_submitted_on(18, "2025-08-24")
# # update_submitted_on(19, "2025-08-24")
# # update_submitted_on(20, "2025-08-24")

# # update_submitted_on(21, "2025-08-31")
# # update_submitted_on(22, "2025-08-31")
# # update_submitted_on(23, "2025-08-31")

import ast
import streamlit as st
from src.feature.helper_requirement_analyzer.requirement_analysis import evaluate_resume

resume_text = """
Software Engineer with 6 years of experience in C#,SQL.
Holds a Bachelor's degree in Computer Science.
Worked with MongoDB and Oracle databases.
Practices clean code principles and pair programming occasionally.
Fluent in oral and written communication in English
"""
# job_requirements_str = "{'Experience': ['Full Stack Developer with 3 years of experience in C#,SQL'], 'Education': ['Bachelor’s degree in Computer Science'], 'TechnicalSkills': ['Strong in ASP.NET Core, MVC, Web API, MS SQL.', 'Experience with Angular or React for front-end development.', 'Familiarity with cloud platforms (Azure/AWS) and Git version control.'], 'Others': ['Project Management skills on Agile scrum', 'Fluent in oral and written communication in English']}"  
job_requirements_str = "{'Experience': ['Full Stack Developer with 3 years of experience in C#,SQL']}"  

    # convert string → dict
job_requirements = ast.literal_eval(job_requirements_str)
summary_text, total_exp, total_score,technicalskills = evaluate_resume(resume_text, job_requirements)
# print("resume_text:------------\n",resume_text)
# print("job_requirements:--------------\n",job_requirements)
# print("skills:-------------\n",technicalskills)
# email = extract_email(resume_text)
# phone = extract_phone(resume_text)
# name = extract_name_from_text(resume_text,email)
#skills = extract_skills_tfidf(resume_text,"\n".join(job_requirements))
# save_candidate(name, email, phone, total_exp, total_score,technicalskills , summary_text, selected_category_id)
# summary_text = summarize_results(results)
# st.subheader("Resume Evaluation Summary")
print(summary_text) 
