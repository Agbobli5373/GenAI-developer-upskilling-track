from gemini_base import GeminiBaseClient

class GeminiProClient(GeminiBaseClient):
    def generate_content(self, prompt):
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        result = self._post("gemini-2.5-pro-preview-05-06:generateContent", data)
        return result["candidates"][0]["content"]["parts"][0]["text"]