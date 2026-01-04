import re
from datetime import datetime
from decimal import Decimal
from .models import Document, ExtractedLineItem, Business

# Simple ledger mapping based on keywords
LEDGER_MAP = {
    'rent': 'Rent Expense',
    'salary': 'Salary Expense',
    'office': 'Office Expense',
    'sale': 'Sales Revenue',
    'purchase': 'Purchases',
    'bank': 'Bank',
}

# GST types
GST_TYPES = ['CGST', 'SGST', 'IGST']

def classify_ledger(vendor_or_description):
    text = vendor_or_description.lower() if vendor_or_description else ''
    for keyword, ledger in LEDGER_MAP.items():
        if keyword in text:
            return ledger
    return 'Uncategorized'

def extract_gst(text):
    gst_rate = None
    tax_amount = None
    rate_match = re.search(r'(\d{1,2})%', text)
    if rate_match:
        gst_rate = rate_match.group(1) + '%'
    amount_match = re.search(r'Amount[:\s]+(\d+\.\d{2})', text)
    if amount_match:
        tax_amount = Decimal(amount_match.group(1))
    return gst_rate, tax_amount

def process_document(doc: Document):
    text = doc.ocr_text or ""
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', line)
        amount_match = re.search(r'(\d+\.\d{2})', line)
        invoice_match = re.search(r'INV[0-9]+', line, re.IGNORECASE)
        vendor_match = re.search(r'Vendor[:\s]+([A-Za-z0-9 &]+)', line)

        if date_match or amount_match or invoice_match or vendor_match:
            try:
                item = ExtractedLineItem(document=doc)
                if date_match:
                    item.date = datetime.strptime(date_match.group(1), "%d/%m/%Y").date()
                if amount_match:
                    item.amount = Decimal(amount_match.group(1))
                if invoice_match:
                    item.invoice_no = invoice_match.group(0)
                vendor_name = vendor_match.group(1) if vendor_match else None
                item.vendor = vendor_name
                item.ledger_account = classify_ledger(vendor_name or line)
                gst_rate, tax_amount = extract_gst(line)
                item.gst_rate = gst_rate
                item.tax_amount = tax_amount
                item.raw = {"raw_line": line}
                item.save()
            except Exception as e:
                print(f"Failed to save line: {line} Error: {e}")
    doc.status = 'processed'
    doc.save()


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
