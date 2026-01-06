import requests
import json
from .base import BaseAIProvider


class OllamaProvider(BaseAIProvider):
    def __init__(self, model="llama3.1"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def extract(self, text: str) -> dict:
        prompt = f"""
You are an expert Indian Chartered Accountant AI.

Extract structured data from the document text below.

Return STRICT JSON only:
{{
  "vendor": "",
  "invoice_no": "",
  "date": "",
  "total_amount": "",
  "tax_amount": "",
  "confidence": 0-100
}}

DOCUMENT TEXT:
{text}
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }   

        response = requests.post(self.url, json=payload, timeout=120)
        response.raise_for_status()

        raw = response.json()["response"]

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {
                "error": "AI output not valid JSON",
                "raw_response": raw
            }
