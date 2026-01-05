from django.urls import path
from . import views
from .api import health

app_name = "core"  # namespacing for reverse() and include()

urlpatterns = [
    # Auth
    path('', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard / Business
    path('index/', views.index, name='index'),
    path('businesses/new/', views.business_create, name='business_create'),
    path('businesses/<int:pk>/', views.business_detail, name='business_detail'),

    # Documents
    path('businesses/<int:business_id>/upload/', views.upload_document, name='upload_document'),
    path('businesses/<int:business_id>/documents/', views.documents_list, name='documents_list'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),

    # API Health
    path('api/health/', health, name='api_health'),
]
