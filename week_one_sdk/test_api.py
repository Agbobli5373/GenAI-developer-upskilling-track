import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    print(f"API key found: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
else:
    print("API key not found! Please check your .env file.")
    print("Make sure you have a .env file with GEMINI_API_KEY=your_actual_api_key")
