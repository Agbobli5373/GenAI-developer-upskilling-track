@echo off
REM Streamlit App Launcher for Gemini AI Assistant
echo 🤖 Starting Gemini AI Assistant...
echo ==================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo Please create a .env file with your API keys:
    echo GOOGLE_API_KEY=your_google_api_key_here
    echo OPENWEATHER_API_KEY=your_openweather_api_key_here
    echo.
    pause
)

REM Start Streamlit app
echo 🚀 Launching Streamlit app...
echo The app will open in your default browser
echo Press Ctrl+C to stop the server
echo.

streamlit run streamlit_app.py
