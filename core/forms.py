from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Business, Document
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# -------------------- BUSINESS FORM --------------------
class BusinessForm(forms.ModelForm):
    pan = forms.CharField(
        required=False,
        max_length=20,
        validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]$', 'Invalid PAN format')],
        widget=forms.TextInput(attrs={'placeholder': 'PAN'})
    )
    gstin = forms.CharField(
        required=False,
        max_length=20,
        validators=[RegexValidator(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', 'Invalid GSTIN format')],
        widget=forms.TextInput(attrs={'placeholder': 'GSTIN'})
    )

    class Meta:
        model = Business
        fields = ['name', 'pan', 'gstin', 'financial_year_start']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Business Name'}),
            'financial_year_start': forms.DateInput(attrs={'type': 'date'}),
        }


# -------------------- DOCUMENT UPLOAD FORM --------------------
class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['file', 'doc_type']
        widgets = {
            'doc_type': forms.Select(),
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        # Validate file size (limit to 10MB)
        max_size = 10 * 1024 * 1024
        if f.size > max_size:
            raise forms.ValidationError(_('File size exceeds 10MB limit.'))
        return f


# -------------------- SIGNUP FORM --------------------
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email already exists."))
        return email


# -------------------- LOGIN FORM --------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "autocomplete": "username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "autocomplete": "current-password"})
    )
