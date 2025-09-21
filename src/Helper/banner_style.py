import streamlit as st


def banner_style(title):
    st.markdown(f"""
    <style>
    .header-banner {{
        background-color: #2e3b70;  /* dark blue background */
        border-radius: 15px;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #7fd3c7;
        margin-bottom: 20px;
    }}

    .header-left {{
        display: flex;
        align-items: center;
    }}

    .header-left img {{
        width: 50px;
        height: 50px;
        margin-right: 15px;
        border-radius: 10px;
    }}

    .header-title {{
        font-size: 28px;
        font-weight: 600;
    }}
    .header-timestamp {{
        font-size: 14px;
        color: #cce0e0;
    }}
    </style>

    <div class="header-banner">
        <div class="header-left">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135714.png" alt="icon">
            <div class="header-title">{title}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)