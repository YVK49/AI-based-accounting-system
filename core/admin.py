from django.contrib import admin
from .models import Business, Document, ExtractedLineItem

admin.site.register(Business)
admin.site.register(Document)
admin.site.register(ExtractedLineItem)
