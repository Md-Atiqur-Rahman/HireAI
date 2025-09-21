
from src.feature.dashboards.test_dasboard import test_dashboard_page
from src.feature.dashboards.dashboard import dashboard_page
from src.feature.multiple_resume_analyzer.multiple_rezume_analyze import multiple_resume_analysis
from src.database.db_job_category import create_category_table
from src.database.db_config import drop_table
from src.database.db_candidates import create_candidates_table
from src.database.db_job_requirements import create_job_requirements_table
from src.Admin.job_category_page import job_category_page
from src.Admin.job_requirment import job_requirements_page

# In main.py or upload_resume.py
from src.feature.resume_analyzer.single_resume_analyzer import resume_uploader

# drop_table("job_requirements")
# drop_table("job_categories")

create_job_requirements_table()
create_candidates_table()
create_category_table()

import streamlit as st

# Sidebar navigation
from streamlit_option_menu import option_menu
import streamlit as st

st.set_page_config(
    page_title="Smart Resume AI",
    page_icon="🚀",
    layout="wide"
)

# --- Session State ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #1e1e2f;
        padding: 20px 10px;
    }

    .sidebar-logo {
        text-align: center;
        margin-bottom: 20px;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        color: #5dade2;
        margin-bottom: 25px;
    }

    .menu-button {
        display: block;
        width: 100%;
        height: 50px;
        text-align: left;
        padding: 10px 18px;
        margin: 8px 0;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        color: white;
        background: linear-gradient(90deg, #3498db, #5dade2);
        border: none;
        cursor: pointer;
        transition: 0.3s;
    }

    .menu-button:hover {
        background: linear-gradient(90deg, #1abc9c, #16a085);
    }

    .menu-button.active {
        background: linear-gradient(90deg, #1abc9c, #16a085) !important;
        box-shadow: 0 0 10px rgba(0, 255, 200, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo"><img src="https://cdn-icons-png.flaticon.com/512/1995/1995574.png" width="120"></div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="sidebar-title">Smart Resume AI</div>', unsafe_allow_html=True)

    def menu_button(label, page_name, icon):
        active_class = "active" if st.session_state.page == page_name else ""
        if st.markdown(f"""
            <button class="menu-button {active_class}" onclick="window.parent.streamlitSetPage('{page_name}')">
                {icon} {label}
            </button>
            """, unsafe_allow_html=True):
            pass  # just rendering the button

    # Menu Buttons
    menu_button("HOME", "home", "🏠")
    menu_button("RESUME ANALYZER", "analyzer", "🔍")
    menu_button("RESUME BUILDER", "builder", "📝")
    menu_button("DASHBOARD", "dashboard", "📊")
    menu_button("JOB SEARCH", "jobs", "🎯")

# --- Page Routing ---
page = st.session_state.page

if page == "home":
    dashboard_page()
elif page == "analyzer":
    resume_uploader()
elif page == "builder":
    st.title("📝 Resume Builder")
elif page == "dashboard":
    st.title("📊 Dashboard")
elif page == "jobs":
    st.title("🎯 Job Search")
