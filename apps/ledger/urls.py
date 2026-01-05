from django.urls import path

from . import views

app_name = 'ledger'

urlpatterns = [
    path('vouchers/', views.VoucherListView.as_view(), name='voucher-list'),
    path('vouchers/create/', views.VoucherCreateView.as_view(), name='voucher-create'),
    path('accounts/', views.AccountListView.as_view(), name='account-list'),
]
