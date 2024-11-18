from django.db import models

# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    user_ref_id = models.CharField(max_length=10, unique=True, primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def get_all_permissions(self, obj=None):
        return super().get_all_permissions(obj)

    def has_perm(self, perm, obj=None):
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return super().has_module_perms(app_label)

    def __str__(self):
        return self.email


class UserDetail(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.CharField(max_length=50)
    organization = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.user_type}"


class OrganizationDetail(models.Model):
    ref_org_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    created_by = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id}"

class SubscriptionDetail(models.Model):
    ref_subscription_id = models.CharField(max_length=50)
    organization = models.ForeignKey(OrganizationDetail, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    is_expired = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id}- {self.expired_at}"
    
class ApplicationDetail(models.Model):
    ref_app_id = models.CharField(max_length=50)
    organization = models.ForeignKey(OrganizationDetail, on_delete=models.CASCADE)
    chat_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id}- {self.organization}"