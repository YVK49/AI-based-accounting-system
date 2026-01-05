from django.db import models
from apps.accounts.models import Business
import uuid

class DocumentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Processing'
    PROCESSING = 'PROCESSING', 'Processing in AI'
    PROCESSED = 'PROCESSED', 'Draft Created'
    FAILED = 'FAILED', 'Processing Failed'
    REVIEWED = 'REVIEWED', 'CA Reviewed'

class DocumentType(models.TextChoices):
    INVOICE = 'INVOICE', 'Purchase Invoice'
    BILL = 'BILL', 'Sales Bill'
    BANK_STATEMENT = 'BANK_STATEMENT', 'Bank Statement'
    OTHER = 'OTHER', 'Other Document'

class UploadedDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    doc_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER)
    
    status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.PENDING)
    ai_metadata = models.JSONField(blank=True, null=True) # Extracted raw data
    
    # Traceability
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.doc_type} - {self.business.name} ({self.status})"
