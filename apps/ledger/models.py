from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models import Organization, Business
import uuid

class FinancialYear(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='financial_years')
    start_date = models.DateField()
    end_date = models.DateField()
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business.name}: {self.start_date.year}-{self.end_date.year}"

class AccountGroup(models.Model):
    """
    Hierarchical groups for the Chart of Accounts.
    Example: Assets -> Current Assets -> Bank Accounts
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subgroups')
    
    # Standard Accounting Classification
    class Classification(models.TextChoices):
        ASSET = 'ASSET', 'Asset'
        LIABILITY = 'LIABILITY', 'Liability'
        EQUITY = 'EQUITY', 'Equity'
        INCOME = 'INCOME', 'Income'
        EXPENSE = 'EXPENSE', 'Expense'
    
    classification = models.CharField(max_length=20, choices=Classification.choices)

    def __str__(self):
        return f"{self.name} ({self.business.name})"

class Account(models.Model):
    """
    The actual Ledger Account.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    group = models.ForeignKey(AccountGroup, on_delete=models.PROTECT, related_name='accounts')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, null=True) # Optional accounting code
    opening_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.name} | {self.group.name}"

class VoucherType(models.TextChoices):
    SALES = 'SALES', 'Sales'
    PURCHASE = 'PURCHASE', 'Purchase'
    PAYMENT = 'PAYMENT', 'Payment'
    RECEIPT = 'RECEIPT', 'Receipt'
    CONTRA = 'CONTRA', 'Contra'
    JOURNAL = 'JOURNAL', 'Journal'

class Voucher(models.Model):
    """
    Header for a transaction.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.PROTECT)
    voucher_type = models.CharField(max_length=20, choices=VoucherType.choices)
    voucher_number = models.CharField(max_length=50) # Auto-generated per type/business
    date = models.DateField()
    narration = models.TextField(blank=True)
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=True) # AI drafts start here
    
    class Meta:
        unique_together = ('business', 'voucher_type', 'voucher_number', 'financial_year')

    def __str__(self):
        return f"{self.voucher_type} #{self.voucher_number} | {self.date}"

class JournalEntry(models.Model):
    """
    Double Entry line items.
    Sum of debits must equal sum of credits for a given Voucher.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='entries')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    
    debit = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    
    def clean(self):
        if self.debit > 0 and self.credit > 0:
            raise ValidationError("A single entry line cannot have both a debit and a credit.")
        if self.debit == 0 and self.credit == 0:
            raise ValidationError("Entry must have either a debit or a credit.")

    def __str__(self):
        return f"{self.account.name}: {self.debit if self.debit > 0 else self.credit}"
