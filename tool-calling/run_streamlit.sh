#!/bin/bash

# Streamlit App Launcher for Gemini AI Assistant
echo "🤖 Starting Gemini AI Assistant..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/Scripts/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your API keys:"
    echo "GOOGLE_API_KEY=your_google_api_key_here"
    echo "OPENWEATHER_API_KEY=your_openweather_api_key_here"
    echo ""
    read -p "Press Enter to continue (the app will show an error until you add the keys)..."
fi

# Start Streamlit app
echo "🚀 Launching Streamlit app..."
echo "The app will open in your default browser"
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run streamlit_app.py
