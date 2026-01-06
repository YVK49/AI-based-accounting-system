from django.shortcuts import render, redirect, get_object_or_404
from .forms import BusinessForm, DocumentUploadForm, SignUpForm, LoginForm
from .models import Business, Document
import pytesseract
from PIL import Image
from django.contrib.auth import login, logout
from .processor import process_document, generate_business_summary
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import authenticate

# -------------------- AUTH VIEWS --------------------
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("core:index"))
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(reverse("core:index"))
    else:
        form = LoginForm()
    return render(request, "core/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse("core:login"))


# -------------------- DASHBOARD / BUSINESS --------------------
@login_required
def index(request):
    businesses = Business.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'core/index.html', {'businesses': businesses})


@login_required
def business_create(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save(commit=False)
            business.created_by = request.user
            business.save()
            return redirect(reverse("core:business_detail", args=[business.id]))
    else:
        form = BusinessForm()
    return render(request, 'core/business_form.html', {'form': form})


@login_required
def business_detail(request, pk):
    business = get_object_or_404(Business, pk=pk, created_by=request.user)
    summary = generate_business_summary(business)
    return render(request, 'core/business_detail.html', {'business': business, 'summary': summary})


# -------------------- DOCUMENTS --------------------
@login_required
def upload_document(request, business_id):
    business = get_object_or_404(Business, pk=business_id, created_by=request.user)
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.business = business
            doc.uploaded_by = request.user
            doc.save()

            # OCR for image files
            try:
                filepath = doc.file.path
                if filepath.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                    text = pytesseract.image_to_string(Image.open(filepath))
                    doc.ocr_text = text
                    doc.status = 'uploaded'
                    doc.save()
                else:
                    doc.ocr_text = 'OCR not run for this file type in MVP.'
                    doc.status = 'uploaded'
                    doc.save()
            except Exception as e:
                doc.ocr_text = f'OCR failed. Error: {e}'
                doc.status = 'ocr_failed'
                doc.save()

            # Process document in background or immediately
            process_document(doc)

            return redirect(reverse("core:documents_list", args=[business.id]))
    else:
        form = DocumentUploadForm()
    return render(request, 'core/upload.html', {'form': form, 'business': business})


@login_required
def documents_list(request, business_id):
    business = get_object_or_404(Business, pk=business_id, created_by=request.user)
    docs = business.documents.all().order_by('-uploaded_at')
    return render(request, 'core/documents_list.html', {'business': business, 'documents': docs})


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(Document, pk=pk, business__created_by=request.user)
    lines = doc.lines.all()
    return render(request, 'core/document_detail.html', {'doc': doc, 'lines': lines})



