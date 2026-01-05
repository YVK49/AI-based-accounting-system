from django.shortcuts import render, redirect, get_object_or_404
from .forms import BusinessForm, DocumentUploadForm, SignUpForm, LoginForm
from .models import Business, Document
import pytesseract
from PIL import Image
from django.contrib.auth import login, logout
from .processor import process_document, generate_business_summary
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = LoginForm()
    return render(request, "core/login.html", {"form": form})


@login_required
def index(request):
    # Only show businesses created by the logged-in user
    businesses = Business.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'core/index.html', {'businesses': businesses})


@login_required
def business_create(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            b.created_by = request.user
            b.save()
            return redirect('business_detail', b.id)
    else:
        form = BusinessForm()
    return render(request, 'core/business_form.html', {'form': form})


@login_required
def business_detail(request, pk):
    # Ensure only owner can access their business
    b = get_object_or_404(Business, pk=pk, created_by=request.user)
    summary = generate_business_summary(b)
    return render(request, 'core/business_detail.html', {'business': b, 'summary': summary})


@login_required
def upload_document(request, business_id):
    # Only allow documents for user's own business
    b = get_object_or_404(Business, pk=business_id, created_by=request.user)
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.business = b
            doc.uploaded_by = request.user
            doc.save()

            # OCR for images
            try:
                fp = doc.file.path
                if fp.lower().endswith(('.png','.jpg','.jpeg','.tiff','.bmp')):
                    text = pytesseract.image_to_string(Image.open(fp))
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

            # Process document
            process_document(doc)

            return redirect('documents_list', b.id)
    else:
        form = DocumentUploadForm()
    return render(request, 'core/upload.html', {'form': form, 'business': b})


@login_required
def documents_list(request, business_id):
    # Only show documents for user's own business
    b = get_object_or_404(Business, pk=business_id, created_by=request.user)
    docs = b.documents.all().order_by('-uploaded_at')
    return render(request, 'core/documents_list.html', {'business': b, 'documents': docs})


@login_required
def document_detail(request, pk):
    # Only allow access if user owns the document's business
    doc = get_object_or_404(Document, pk=pk, business__created_by=request.user)
    lines = doc.lines.all()
    return render(request, 'core/document_detail.html', {'doc': doc, 'lines': lines})
