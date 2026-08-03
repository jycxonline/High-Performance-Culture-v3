@echo off
cd /d "%~dp0"
if not exist .venv (
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)
echo Starting High Performance Diagnostic Tool at http://localhost:8501
streamlit run app.py
pause
