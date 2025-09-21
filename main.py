import streamlit as st
from src.Admin.job_requirment import job_requirements_page
from src.feature.dashboards.test_dasboard import test_dashboard_page
from src.feature.dashboards.dashboard import dashboard_page
from src.feature.multiple_resume_analyzer.multiple_rezume_analyze import multiple_resume_analysis
from src.feature.resume_analyzer.single_resume_analyzer import resume_uploader
from src.Admin.job_category_page import job_category_page

st.set_page_config(page_title="Hire AI", page_icon="https://cdn-icons-png.flaticon.com/512/3135/3135714.png", layout="wide")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Sidebar CSS
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #1e1e2f;
    padding: 20px 10px;
}
.sidebar-logo {text-align:center;margin-bottom:20px;}
.sidebar-title {font-size:22px;font-weight:bold;text-align:center;color:#5dade2;margin-bottom:25px;}

/* Make all buttons same size */
[data-testid="stSidebar"] .stButton>button {
    width: 200px !important; /* fixed width */
    height: 50px !important; /* fixed height */
    margin: 8px 0 !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    text-align: left;
    color: white !important;
    background: linear-gradient(90deg, #3498db, #5dade2) !important;
    border: none !important;
    transition: 0.3s !important;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background: linear-gradient(90deg, #1abc9c, #16a085) !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar menu
with st.sidebar:
    st.markdown('<div class="sidebar-logo"><img src="https://cdn-icons-png.flaticon.com/512/3135/3135714.png" width="120"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Hire AI</div>', unsafe_allow_html=True)

    menu_items = {
        "📊 DASHBOARD": "dashboard",             # Dashboard overview
        "🔍 RESUME ANALYZER": "analyzer",        # Analyze a single resume
        "🗂️ All RESUME ANALYZER": "allanalyzer", # Analyze multiple resumes
        "➕ Add Requirements": "JobRequirements", # Add new job requirements
        "🏷️ Add Categories": "JobCategories"     # Add new job categories
    }


    for label, page_name in menu_items.items():
        btn_key = f"btn_{page_name}"
        clicked = st.button(label, key=btn_key)
        if clicked:
            st.session_state.page = page_name

# Page routing
page = st.session_state.page
if page == "dashboard":
    test_dashboard_page()
    # dashboard_page()
elif page == "analyzer":
    resume_uploader()
elif page == "allanalyzer":
    multiple_resume_analysis()
elif page == "JobRequirements":
    job_requirements_page()
elif page == "JobCategories":
    job_category_page()
