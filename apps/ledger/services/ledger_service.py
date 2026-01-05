from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import Voucher, JournalEntry, Account, FinancialYear

class LedgerService:
    @staticmethod
    @transaction.atomic
    def create_voucher(business, voucher_data, entries_data):
        """
        voucher_data: {date, type, number, fy_id, narration}
        entries_data: [{account_id, debit, credit}, ...]
        """
        # 1. FY Check
        fy = FinancialYear.objects.get(id=voucher_data['fy_id'])
        if fy.is_locked:
            raise ValidationError("Cannot create vouchers in a locked Financial Year.")

        # 2. Date Validation (Must be within FY)
        if not (fy.start_date <= voucher_data['date'] <= fy.end_date):
            raise ValidationError(f"Voucher date must be within {fy.start_date} and {fy.end_date}.")

        # 3. Create Voucher Header
        voucher = Voucher.objects.create(
            business=business,
            financial_year=fy,
            voucher_type=voucher_data['voucher_type'],
            voucher_number=voucher_data['voucher_number'],
            date=voucher_data['date'],
            narration=voucher_data.get('narration', ''),
            is_draft=voucher_data.get('is_draft', False)
        )

        # 4. Create Entries and Validate Totals
        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')

        for entry in entries_data:
            acc = Account.objects.get(id=entry['account_id'], business=business)
            
            amount_dr = Decimal(str(entry.get('debit', 0)))
            amount_cr = Decimal(str(entry.get('credit', 0)))

            JournalEntry.objects.create(
                voucher=voucher,
                account=acc,
                debit=amount_dr,
                credit=amount_cr
            )
            
            total_debit += amount_dr
            total_credit += amount_cr

        # 5. Final Double Entry Check
        if total_debit != total_credit:
            raise ValidationError(f"Unbalanced Voucher: Total Debit ({total_debit}) must equal Total Credit ({total_credit}).")

        return voucher

    @staticmethod
    def get_account_balance(account_id):
        # Service logic for calculating real-time balance
        entries = JournalEntry.objects.filter(account_id=account_id)
        totals = entries.aggregate(
            dr_sum=Sum('debit'),
            cr_sum=Sum('credit')
        )
        opening = Account.objects.get(id=account_id).opening_balance
        
        balance = opening + (totals['dr_sum'] or Decimal('0.00')) - (totals['cr_sum'] or Decimal('0.00'))
        return balance
