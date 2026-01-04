from django.utils import timezone
from decimal import Decimal
from apps.ai_bridge.services.ai_service import AIService
from apps.ledger.models import Account, FinancialYear, VoucherType
from apps.ledger.services.ledger_service import LedgerService
from ..models import UploadedDocument, DocumentStatus, DocumentType

class DocumentProcessingService:
    @staticmethod
    def process_document(document_id):
        """
        Orchestrates the conversion of a document to a draft voucher.
        """
        doc = UploadedDocument.objects.get(id=document_id)
        doc.status = DocumentStatus.PROCESSING
        doc.save()

        try:
            # 1. AI Extraction
            ai_data = AIService.process_document(doc)
            
            # 2. Get Ledger Context
            # Find appropriate accounts based on AI suggestion
            # In a real system, we'd have a mapping layer or fuzzy search
            purchase_account = Account.objects.filter(
                business=doc.business, 
                name__icontains=ai_data.get('suggested_ledger', 'Purchase')
            ).first()
            
            tax_account = Account.objects.filter(
                business=doc.business,
                name__icontains='GST'
            ).first()
            
            # Default to a Suspense/Vendor account if not found
            vendor_account = Account.objects.filter(
                business=doc.business,
                name__icontains=ai_data.get('vendor_name')
            ).first()

            if not purchase_account or not vendor_account:
                # We stop here for manual review if critical accounts aren't identified
                doc.status = DocumentStatus.FAILED
                doc.ai_metadata['error'] = "Could not confidently map to ledger accounts."
                doc.save()
                return False

            # 3. Determine Financial Year
            doc_date = timezone.datetime.strptime(ai_data['invoice_date'], '%Y-%m-%d').date()
            fy = FinancialYear.objects.filter(
                business=doc.business,
                start_date__lte=doc_date,
                end_date__gte=doc_date
            ).first()

            if not fy:
                raise ValueError(f"No Financial Year found for date {doc_date}")

            # 4. Create Draft Voucher via LedgerService
            voucher_data = {
                'date': doc_date,
                'voucher_type': VoucherType.PURCHASE if doc.doc_type == DocumentType.INVOICE else VoucherType.JOURNAL,
                'voucher_number': f"AI-{doc.id.hex[:6].upper()}",
                'fy_id': fy.id,
                'narration': f"AI Draft from uploaded document. Extracted Vendor: {ai_data['vendor_name']}",
                'is_draft': True
            }

            total_amt = Decimal(str(ai_data['total_amount']))
            tax_amt = Decimal(str(ai_data['gst_amount']))
            net_amt = total_amt - tax_amt

            entries = [
                {'account_id': purchase_account.id, 'debit': net_amt, 'credit': 0},
                {'account_id': vendor_account.id, 'debit': 0, 'credit': total_amt},
            ]
            
            if tax_amt > 0 and tax_account:
                entries.append({'account_id': tax_account.id, 'debit': tax_amt, 'credit': 0})

            voucher = LedgerService.create_voucher(doc.business, voucher_data, entries)
            
            # 5. Link document to voucher (if we add a FK to Voucher later)
            doc.status = DocumentStatus.PROCESSED
            doc.processed_at = timezone.now()
            doc.save()
            
            return voucher

        except Exception as e:
            doc.status = DocumentStatus.FAILED
            doc.ai_metadata = doc.ai_metadata or {}
            doc.ai_metadata['error'] = str(e)
            doc.save()
            raise e
