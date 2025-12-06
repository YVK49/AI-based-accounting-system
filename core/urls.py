from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('businesses/new/', views.business_create, name='business_create'),
    path('businesses/<int:pk>/', views.business_detail, name='business_detail'),
    path('businesses/<int:business_id>/upload/', views.upload_document, name='upload_document'),
    path('businesses/<int:business_id>/documents/', views.documents_list, name='documents_list'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
]

from django.urls import path
from .api import health

urlpatterns += [path('api/health/', health)]
