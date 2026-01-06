import re
from datetime import datetime
from decimal import Decimal
from .models import Document, ExtractedLineItem, Business
from apps.ai_bridge.services.ai_service import AIService
import pytesseract

ai_service = AIService()

# ---------- LEDGER KEYWORDS ----------
LEDGER_MAP = {
    'rent': 'Rent Expense',
    'salary': 'Salary Expense',
    'office': 'Office Expense',
    'sale': 'Sales Revenue',
    'purchase': 'Purchases',
    'bank': 'Bank',
}

GST_TYPES = ['CGST', 'SGST', 'IGST']

def classify_ledger(vendor_or_description):
    text = vendor_or_description.lower() if vendor_or_description else ''
    for keyword, ledger in LEDGER_MAP.items():
        if keyword in text:
            return ledger
    return 'Uncategorized'

def extract_gst(text):
    """Try to extract GST rate and tax amount from a line"""
    gst_rate = None
    tax_amount = None

    # Flexible GST pattern: e.g., CGST 5%, SGST 5%, IGST 12%
    rate_match = re.search(r'(\d{1,2})\s*%', text)
    if rate_match:
        gst_rate = rate_match.group(1) + '%'

    # Amount patterns: "Amount 123.45", "Total: 123.45"
    amount_match = re.search(r'(?:Amount|Total|Tax|Rs\.?)[:\s]+(\d+\.\d{2})', text, re.IGNORECASE)
    if amount_match:
        tax_amount = Decimal(amount_match.group(1))

    return gst_rate, tax_amount

def process_document(doc: Document):
    text = doc.ocr_text or ""

    # ---------- DEBUG: Show OCR ----------
    print(f"\n=== OCR TEXT FOR DOCUMENT {doc.id} ===")
    print(text)
    print("=== END OCR TEXT ===\n")

    # ---------- AI STEP ----------
    ai_data = {}
    try:
        ai_data = ai_service.process_document(text)
    except Exception as e:
        ai_data = {"error": str(e)}

    # ---------- SPLIT LINES ----------
    lines = text.split("\n")

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        print(f"Processing line: {line}")  # DEBUG: show each line

        # Common patterns on receipts
        date_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', line)
        amount_match = re.findall(r'\d+\.\d{2}', line)  # get all amounts
        invoice_match = re.search(r'(?:INV|Invoice)\s*[:\s]*([A-Za-z0-9-]+)', line, re.IGNORECASE)
        vendor_match = re.search(r'(?:Vendor|From|Bill From)[:\s]*([A-Za-z0-9 &]+)', line, re.IGNORECASE)

        # Only save if some data exists
        if date_match or amount_match or invoice_match or vendor_match:
            try:
                item = ExtractedLineItem(document=doc)

                # Date
                if date_match:
                    try:
                        item.date = datetime.strptime(date_match.group(1).replace('-', '/'), "%d/%m/%Y").date()
                    except:
                        item.date = None

                # Amount: take last one on line (usually total)
                if amount_match:
                    item.amount = Decimal(amount_match[-1])

                # Invoice
                if invoice_match:
                    item.invoice_no = invoice_match.group(1)

                # Vendor
                vendor_name = vendor_match.group(1) if vendor_match else None
                item.vendor = vendor_name

                # Ledger
                item.ledger_account = classify_ledger(vendor_name or line)

                # GST extraction
                gst_rate, tax_amount = extract_gst(line)
                item.gst_rate = gst_rate
                item.tax_amount = tax_amount

                # Save raw + AI suggestions
                item.raw = {
                    "raw_line": line,
                    "ai_suggestion": ai_data
                }

                item.save()
                print(f"Saved line item: {item}")  # DEBUG: success
            except Exception as e:
                print(f"Failed to save line: {line} | Error: {e}")

    doc.status = "processed"
    doc.save()
    print(f"Document {doc.id} processed successfully!\n")


def generate_business_summary(business: Business):
    ledger_totals = {}
    gst_totals = {}
    total_income = Decimal('0')
    total_expense = Decimal('0')

    for doc in business.documents.all():
        for line in doc.lines.all():
            ledger = line.ledger_account or 'Uncategorized'
            ledger_totals[ledger] = ledger_totals.get(ledger, Decimal('0')) + (line.amount or 0)
            gst_rate = line.gst_rate or 'No GST'
            gst_totals[gst_rate] = gst_totals.get(gst_rate, Decimal('0')) + (line.tax_amount or 0)
            if 'Revenue' in ledger:
                total_income += line.amount or 0
            else:
                total_expense += line.amount or 0

    net_profit = total_income - total_expense

    return {
        'ledger_totals': ledger_totals,
        'gst_totals': gst_totals,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit
    }