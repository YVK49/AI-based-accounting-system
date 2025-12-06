from django import forms
from .models import Business, Document

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'pan', 'gstin', 'financial_year_start']

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'doc_type']
