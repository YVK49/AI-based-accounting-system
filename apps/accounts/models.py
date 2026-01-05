from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class Organization(models.Model):
    """
    Represents a CA Firm (The Tenant)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True) # e.g. ICAI Membership/Firm Reg
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Business(models.Model):
    """
    A Client Business managed by a CA Firm
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=255)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    pan = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Businesses"

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class UserRole(models.TextChoices):
    CA_PRINCIPAL = 'CA_PRINCIPAL', 'CA Principal'
    CA_SENIOR = 'CA_SENIOR', 'Senior Accountant'
    CA_JUNIOR = 'CA_JUNIOR', 'Junior Accountant'
    BUSINESS_ADMIN = 'BUSINESS_ADMIN', 'Business Admin'
    BUSINESS_VIEWER = 'BUSINESS_VIEWER', 'Business Viewer'

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CA_JUNIOR)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

class SubscriptionPlan(models.TextChoices):
    BASIC = 'BASIC', 'Basic'
    ADVANCED = 'ADVANCED', 'Advanced'
    PREMIUM = 'PREMIUM', 'Premium'

class License(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='license')
    plan = models.CharField(max_length=20, choices=SubscriptionPlan.choices, default=SubscriptionPlan.BASIC)
    expires_at = models.DateTimeField()
    
    # Feature Flags
    ai_automation_enabled = models.BooleanField(default=False)
    audit_intelligence_enabled = models.BooleanField(default=False)
    max_businesses = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.organization.name} - {self.plan}"
