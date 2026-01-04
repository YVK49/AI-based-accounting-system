from .base import AIProvider
from decimal import Decimal

class MockAIProvider(AIProvider):
    def extract_invoice_data(self, file_path):
        # Simulated OCR and LLM Extraction
        return {
            "vendor_name": "Generic Supplier Ltd",
            "invoice_date": "2026-01-04",
            "total_amount": 1180.00,
            "gst_amount": 180.00,
            "tax_rate": 18.0,
            "suggested_ledger": "Purchase Account"
        }

    def classify_transaction(self, narration):
        return "Conveyance Expense"

    def generate_compliance_explanation(self, context_data):
        return "The tax liability increased because of higher interstate sales compared to previous month."
