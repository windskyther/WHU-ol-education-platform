from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin", "Admin"),
    )

    MOOD_CHOICES = (
        ("happy", "Happy"),
        ("studying", "Studying"),
        ("slacking", "Slacking"),
        ("focused", "Focused"),
        ("tired", "Tired"),
        ("excited", "Excited"),
        ("coding", "Coding"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="student", db_index=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    mood = models.CharField(max_length=16, choices=MOOD_CHOICES, default="happy", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"


class EmailVerificationCode(models.Model):
    PURPOSE_CHOICES = (
        ("register", "Register"),
    )

    email = models.EmailField(db_index=True)
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES, default="register")
    expires_at = models.DateTimeField(db_index=True)
    is_used = models.BooleanField(default=False, db_index=True)
    attempt_count = models.PositiveIntegerField(default=0)
    request_ip = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["email", "purpose", "expires_at", "is_used"]),
        ]

    def __str__(self):
        return f"{self.email} {self.purpose}"


def ensure_user_profile(user, role="student"):
    if user.is_superuser:
        role = "admin"
    profile, _ = UserProfile.objects.get_or_create(user=user, defaults={"role": role})
    return profile
