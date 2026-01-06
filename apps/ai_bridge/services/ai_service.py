import json
import os

class AIService:
    """
    Dummy AI service for now.
    Later this will call real AI APIs (OpenAI, etc).
    """

    def process_document(self, text: str) -> dict:
        """
        Takes OCR text and returns structured data.
        """
        # MOCK AI OUTPUT (SAFE FOR NOW)
        return {
            "vendor": None,
            "invoice_no": None,
            "date": None,
            "amount": None,
            "gst_rate": None,
            "tax_amount": None,
            "confidence": 0.60
        }
