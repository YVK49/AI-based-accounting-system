from django.contrib import admin
from .models import Business, Document, ExtractedLineItem

# -------------------- BUSINESS ADMIN --------------------
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'financial_year_start', 'created_at')
    list_filter = ('created_by', 'financial_year_start')
    search_fields = ('name', 'pan', 'gstin')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ('created_by',)  # Faster for many users

# -------------------- DOCUMENT ADMIN --------------------
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'uploaded_by', 'doc_type', 'status', 'uploaded_at')
    list_filter = ('doc_type', 'status', 'uploaded_at')
    search_fields = ('business__name', 'uploaded_by__username')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)
    autocomplete_fields = ('business', 'uploaded_by')

# -------------------- LINE ITEM ADMIN --------------------
@admin.register(ExtractedLineItem)
class ExtractedLineItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'vendor', 'amount', 'tax_amount', 'invoice_no', 'ledger_account')
    list_filter = ('ledger_account',)
    search_fields = ('vendor', 'invoice_no', 'ledger_account')
    ordering = ('-id',)
    autocomplete_fields = ('document',)
