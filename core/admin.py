from django.contrib import admin
from .models import Business, Document, ExtractedLineItem


# =====================================================
# 🔥 CUSTOM BUSINESS FILTERS
# =====================================================

class BusinessFilter(admin.SimpleListFilter):
    title = 'Business'
    parameter_name = 'business'

    def lookups(self, request, model_admin):
        return [(b.id, b.name) for b in Business.objects.all().only('id', 'name')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(id=self.value())
        return queryset


class DocumentBusinessFilter(admin.SimpleListFilter):
    title = 'Business'
    parameter_name = 'business'

    def lookups(self, request, model_admin):
        return [(b.id, b.name) for b in Business.objects.all().only('id', 'name')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(business__id=self.value())
        return queryset


class LineItemBusinessFilter(admin.SimpleListFilter):
    title = 'Business'
    parameter_name = 'business'

    def lookups(self, request, model_admin):
        return [(b.id, b.name) for b in Business.objects.all().only('id', 'name')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(document__business__id=self.value())
        return queryset


# =====================================================
# 🏢 BUSINESS ADMIN
# =====================================================

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'created_by', 'owner',
        'financial_year_start', 'financial_year_end',
        'status', 'is_active', 'created_at'
    )

    list_filter = (
        BusinessFilter,       # 🔥 Filter by business name
        'status',
        'is_active',
        'financial_year_start'
    )

    search_fields = ('name', 'pan', 'gstin')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'last_draft_generated_at')
    autocomplete_fields = ('created_by', 'owner')


# =====================================================
# 📄 DOCUMENT ADMIN
# =====================================================

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'business', 'uploaded_by',
        'doc_type', 'document_number',
        'is_processed', 'uploaded_at'
    )

    list_filter = (
        DocumentBusinessFilter,   # 🔥 Filter by business name
        'doc_type',
        'is_processed',
        'uploaded_at'
    )

    search_fields = ('document_number', 'business__name')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)
    autocomplete_fields = ('business', 'uploaded_by')


# =====================================================
# 📊 EXTRACTED LINE ITEM ADMIN
# =====================================================

@admin.register(ExtractedLineItem)
class ExtractedLineItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'document', 'vendor',
        'amount', 'tax_amount',
        'ledger_account', 'is_verified'
    )

    list_filter = (
        LineItemBusinessFilter,  # 🔥 Filter by business name
        'ledger_account',
        'is_verified'
    )

    search_fields = ('vendor', 'invoice_no', 'ledger_account')
    ordering = ('-id',)
    autocomplete_fields = ('document',)
