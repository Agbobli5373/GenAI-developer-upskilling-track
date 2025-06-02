import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

logger = logging.getLogger("gemini_utils")

class GeminiAPIError(Exception):
    pass

def get_api_key():
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in environment.")
        raise GeminiAPIError("API key not found.")
    return GEMINI_API_KEY

def chat_with_gemini(prompt):
    api_key = get_api_key()
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = httpx.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 429:
            raise GeminiAPIError("Rate limit exceeded. Please try again later.")
        raise GeminiAPIError(f"HTTP error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise GeminiAPIError("An unexpected error occurred.")