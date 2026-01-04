# AI Accounting MVP (Django + SQLite)

This is a minimal MVP scaffold for the AI accounting SaaS you approved.
It includes:
- Django project `acctproj`
- app `core` with Business, Document and simple OCR ingestion
- Simple UI to register a business, upload documents and view extracted OCR text
- Synchronous processing (for MVP). Replace with Celery for production.

## Quick start (local)

1. Create a Python virtualenv and activate it (Python 3.11+ recommended)
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Install Tesseract OCR (system package). On Ubuntu:
   ```
   sudo apt update
   sudo apt install -y tesseract-ocr
   ```
   If tesseract is not installed, uploaded documents will store a placeholder message.

3. Run migrations and start server:
   ```
   python manage.py migrate
   python manage.py runserver
   ```

4. Open http://127.0.0.1:8000/ in your browser.
   - Register a business at `/businesses/new/`
   - Upload documents at `/businesses/<id>/upload/`
   - View documents list at `/businesses/<id>/documents/`

## Notes
- DB: SQLite for MVP (`db.sqlite3`)
- This scaffold is intentionally minimal. Next steps after you review:
  - Add ledger models and mapping rules
  - Add bank statement parsers and reconciliation
  - Add background jobs (Celery/Redis) and move OCR off the request thread
  - Add authentication and role management for CAs
