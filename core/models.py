from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Business(models.Model):
    name = models.CharField(max_length=200)
    pan = models.CharField(max_length=20, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    financial_year_start = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


def upload_to(instance, filename):
    return f"business_{instance.business.id}/documents/{filename}"


class Document(models.Model):
    DOC_TYPES = [
        ('receipt','Receipt/Invoice'),
        ('bank','Bank Statement'),
        ('other','Other'),
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    file = models.FileField(upload_to=upload_to)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES, default='receipt')
    status = models.CharField(max_length=50, default='uploaded')
    ocr_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document {self.id} - {self.business.name}"


class ExtractedLineItem(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='lines')
    date = models.DateField(null=True, blank=True)
    vendor = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    gst_rate = models.CharField(max_length=20, blank=True, null=True)
    invoice_no = models.CharField(max_length=200, blank=True, null=True)
    ledger_account = models.CharField(max_length=100, blank=True, null=True)
    raw = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Line {self.id} ({self.vendor} - {self.amount})"
