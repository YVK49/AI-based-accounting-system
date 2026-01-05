from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone

User = get_user_model()


class Business(models.Model):
    # -------- EXISTING FIELDS (UNCHANGED) --------
    name = models.CharField(max_length=200)
    pan = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]$', 'Invalid PAN format')]
    )
    gstin = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
            'Invalid GSTIN format'
        )]
    )
    financial_year_start = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='businesses'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # -------- 🔥 NEW ADDITIONS --------
    financial_year_end = models.DateField(blank=True, null=True)

    is_active = models.BooleanField(default=True)  # currently working status

    last_draft_generated_at = models.DateTimeField(blank=True, null=True)

    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='owned_businesses',
        help_text="Actual business owner / client"
    )

    BUSINESS_STATUS = [
        ('onboarding', 'Onboarding'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=BUSINESS_STATUS,
        default='onboarding'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['owner']),
            models.Index(fields=['status']),
            models.Index(fields=['financial_year_start']),
        ]

    def __str__(self):
        return self.name


def upload_to(instance, filename):
    return f"business_{instance.business.id}/documents/{filename}"


class Document(models.Model):
    # -------- EXISTING FIELDS (UNCHANGED) --------
    DOC_TYPES = [
        ('receipt', 'Receipt/Invoice'),
        ('bank', 'Bank Statement'),
        ('other', 'Other'),
    ]

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name='documents'
    )
    uploaded_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    file = models.FileField(
        upload_to=upload_to,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff']
        )]
    )
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES, default='receipt')
    status = models.CharField(max_length=50, default='uploaded')
    ocr_text = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # -------- 🔥 NEW ADDITIONS --------
    document_number = models.CharField(
        max_length=100, blank=True, null=True, help_text="Invoice / reference number"
    )

    document_date = models.DateField(blank=True, null=True)

    is_processed = models.BooleanField(default=False)

    checksum = models.CharField(
        max_length=64, blank=True, null=True,
        help_text="Used to detect duplicate uploads"
    )

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['business']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['doc_type']),
            models.Index(fields=['document_number']),
        ]

    def __str__(self):
        return f"Document {self.id} - {self.business.name}"


class ExtractedLineItem(models.Model):
    # -------- EXISTING FIELDS (UNCHANGED) --------
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='lines'
    )
    date = models.DateField(null=True, blank=True)
    vendor = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    gst_rate = models.CharField(max_length=20, blank=True, null=True)
    invoice_no = models.CharField(max_length=200, blank=True, null=True)
    ledger_account = models.CharField(max_length=100, blank=True, null=True)
    raw = models.JSONField(default=dict, blank=True)

    # -------- 🔥 NEW ADDITIONS --------
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['vendor']),
            models.Index(fields=['invoice_no']),
            models.Index(fields=['ledger_account']),
        ]

    def __str__(self):
        return f"Line {self.id} ({self.vendor or 'Unknown'} - {self.amount or 0})"
