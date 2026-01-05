from django.core.exceptions import PermissionDenied
from apps.common.views.base import ApiView
from ..models import Voucher, Account, AccountGroup, FinancialYear
from ..services.ledger_service import LedgerService
import json

class VoucherListView(ApiView):
    def get(self, request):
        if not request.business:
            return self.error_response("Business context required", status=400)
            
        vouchers = Voucher.objects.filter(business=request.business).prefetch_related('entries')
        
        data = []
        for v in vouchers:
            data.append({
                "id": str(v.id),
                "type": v.voucher_type,
                "number": v.voucher_number,
                "date": v.date.isoformat(),
                "narration": v.narration,
                "is_draft": v.is_draft,
                "entries": [
                    {
                        "account": e.account.name,
                        "debit": str(e.debit),
                        "credit": str(e.credit)
                    } for e in v.entries.all()
                ]
            })
            
        return self.success_response(data)

class VoucherCreateView(ApiView):
    def post(self, request):
        if not request.business:
            return self.error_response("Business context required", status=400)
            
        body = self.get_json_body()
        
        # In a real app, we'd use a Validator class here
        # For brevity, calling service directly
        try:
            voucher = LedgerService.create_voucher(
                business=request.business,
                voucher_data={
                    "date": body['date'],
                    "voucher_type": body['type'],
                    "voucher_number": body['number'],
                    "fy_id": body['fy_id'],
                    "narration": body.get('narration', ''),
                    "is_draft": body.get('is_draft', False)
                },
                entries_data=body['entries']
            )
            return self.success_response({"id": str(voucher.id), "number": voucher.voucher_number}, status=201)
        except KeyError as e:
            return self.error_response(f"Missing field: {str(e)}")

class AccountListView(ApiView):
    def get(self, request):
        if not request.business:
            return self.error_response("Business context required", status=400)
            
        accounts = Account.objects.filter(business=request.business).select_related('group')
        data = [{
            "id": str(a.id),
            "name": a.name,
            "group": a.group.name,
            "classification": a.group.classification,
            "balance": str(LedgerService.get_account_balance(a.id))
        } for a in accounts]
        
        return self.success_response(data)
