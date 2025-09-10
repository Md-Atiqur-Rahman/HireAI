
@echo off
REM Activate virtual environment
call env\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Run the Streamlit app
streamlit run app.py
