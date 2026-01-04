from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/ledger/', include('apps.ledger.urls')),
    path('api/v1/compliance/', include('apps.compliance.urls')),
]
