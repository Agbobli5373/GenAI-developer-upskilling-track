from gemini_base import GeminiBaseClient

class GeminiFlashClient(GeminiBaseClient):
    def generate_content(self, prompt):
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        result = self._post("gemini-2.0-flash:generateContent", data)
        return result["candidates"][0]["content"]["parts"][0]["text"]