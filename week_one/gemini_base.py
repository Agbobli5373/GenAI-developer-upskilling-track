import os
import httpx
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

class GeminiBaseClient(ABC):
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/"
        if not self.api_key:
            raise ValueError("API key required")

    @abstractmethod
    def generate_content(self, prompt):
        pass

    def _post(self, endpoint, data):
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        response = httpx.post(self.base_url + endpoint, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        return response.json()