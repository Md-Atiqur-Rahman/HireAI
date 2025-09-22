import streamlit as st

def home_page():
    # ✅ Page config
    st.set_page_config(page_title="Hire AI", layout="wide")

    # --- Hero Banner ---
    st.markdown("""
        <div style="background-color:#1a1a1a;padding:70px 30px;border-radius:12px;
                    text-align:center;box-shadow:0 6px 18px rgba(0,0,0,0.6);">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135714.png" 
                 alt="Hire AI Logo" width="100" style="margin-bottom:20px;">
            <h1 style="color:white;font-size:52px;margin-bottom:25px;">Hire AI</h1>
            <p style="color:#dcdcdc;font-size:20px;line-height:1.7;max-width:900px;margin:0 auto;">
                Automate resume shortlisting with intelligent analysis.<br>
                Empower your hiring process with AI that reviews and ranks resumes in seconds — 
                saving time, improving accuracy, and finding the best-fit candidates faster.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- Section: AI-Powered Analysis ---
    st.markdown("""
        <div style="background-color:#F5F7FA;padding:50px 30px;border-radius:12px;text-align:center;">
            <h2 style="color:#333;font-size:32px;margin-bottom:15px;">⚡ AI-Powered Resume Analysis</h2>
            <p style="color:#555;font-size:18px;line-height:1.7;max-width:850px;margin:0 auto;text-align: justify;">
                Hire AI intelligently evaluates each resume — whether uploaded singly or in batches — 
                by comparing it with the job criteria. It highlights <b>matched</b> and <b>unmatched</b> qualifications,
                and generates a relevance score to help recruiters make faster, data-driven shortlisting decisions.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- Section: Dashboard Insights ---
    st.markdown("""
        <div style="background-color:#F5F7FA;padding:50px 30px;border-radius:12px;text-align:center;">
            <h2 style="color:#333;font-size:32px;margin-bottom:15px;">📊 Smart Resume AI Dashboard</h2>
            <p style="color:#555;font-size:18px;line-height:1.7;max-width:850px;margin:0 auto;text-align: justify;">
                Visualize candidate data in real-time with the Smart Resume AI Dashboard. Track submission trends,
                compare candidate scores, and discover top talent at a glance. With intuitive charts and metrics,
                you’ll gain actionable insights that make hiring decisions more effective and transparent.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- Footer ---
    st.markdown("""
        <div style="text-align:center;padding:20px;color:#aaa;font-size:14px;">
            © 2025 Hire AI · Designed for smarter hiring
        </div>
    """, unsafe_allow_html=True)
