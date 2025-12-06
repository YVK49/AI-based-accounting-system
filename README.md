
# AI-Based Accounting System

An AI-powered accounting SaaS system designed to automate core accounting tasks, reducing manual effort for businesses and accountants. This system leverages OCR, AI-based transaction categorization, and intelligent suggestions to streamline financial workflows.


## Table of Contents

- [Features](#features)
- [Usage](#usage)
- [Support](#support)
- [License](#license)

---

## Features

### 1. Document Processing
- Reads invoices, receipts, bills, and bank statements using OCR.
- Extracts key details like amounts, dates, GST numbers, and vendor/customer info.
- Primary OCR: **Tesseract**, fallback: **Textract** (cloud-based).

### 2. Ledger & Transaction Management
- Automatically creates and updates ledger accounts.
- Categorizes transactions using AI suggestions.
- Performs **basic bank reconciliation**:
  - Matches bank transactions with ledger entries.
  - Flags discrepancies for manual review.

### 3. GST & ITR Preparation
- Prepares GST summaries from ledger entries.
- Drafts ITR-ready data for filing.
- Future goal: fully automated GST/ITR e-filing.

### 4. AI Intelligence
- Suggests categorizations for unclear transactions.
- Detects inconsistencies and anomalies in entries.
- Learns over time to handle complex accounting rules.

---

## Tech Stack
- **Backend:** Python, Django  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** PostgreSQL / Django ORM  
- **Others:** Git/GitHub, free API integrations for OCR and parsing  

---

## Project Status
- **Current:** Handles routine accounting tasks like ledger entries, transaction categorization, and bank reconciliation. Draft GST/ITR data generation works.  
- **Pending / Next Version:**  
  - Full automation of GST/ITR filing  
  - Advanced exception handling  
  - Predictive insights and financial analytics  
  - Multi-platform support (mobile/web dashboards)  
  - Integration with banks and third-party accounting tools  

---

## Contribution Guidelines & Alerts

**⚠️ Important Notices:**  
1. Do **NOT modify the code directly** on the main branch. Wait for all commits to be reviewed and merged.  
2. Always create a new branch for your features or bug fixes:  
```bash
git checkout -b feature/your-feature-name


## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Steps

1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-accounting.git
cd ai-accounting
```

2. Create a virtual environment

```bash
python -m venv venv
```

3. Activate the environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

4. Install dependencies

```bash
pip install -r requirements.txt
```

5. Run migrations

```bash
python manage.py migrate
```

6. Start the development server

```bash
python manage.py runserver
```

## Usage

After starting the development server, navigate to `http://localhost:8000` in your web browser to access the application.

## Support

For any issues or inquiries:

- **Email:** vamshikrishna8330.com
- **GitHub Issues:** [Link to Issues](https://github.com/YVK49/AI-based-accounting-system/issues)

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
