import hashlib
import secrets
import smtplib
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import status

from apps.common.exceptions import BusinessError
from apps.users.models import EmailVerificationCode, ensure_user_profile


User = get_user_model()


def hash_email_code(email, code):
    return hashlib.sha256(f"{email.lower()}:{code}".encode("utf-8")).hexdigest()


def _uses_smtp_backend():
    return settings.EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend"


def _validate_smtp_settings():
    if not _uses_smtp_backend():
        return

    placeholders = {
        "",
        "smtp.example.com",
        "your_email@example.com",
        "your_email_auth_code",
    }
    required_values = {
        settings.EMAIL_HOST,
        settings.EMAIL_HOST_USER,
        settings.EMAIL_HOST_PASSWORD,
        settings.DEFAULT_FROM_EMAIL,
    }
    if required_values & placeholders:
        raise BusinessError(5000, "EMAIL_SMTP_NOT_CONFIGURED", status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_register_email_code(email, request_ip=""):
    email = email.strip().lower()
    if User.objects.filter(email=email).exists():
        raise BusinessError(4090, "EMAIL_EXISTS", status.HTTP_409_CONFLICT)

    latest = (
        EmailVerificationCode.objects.filter(email=email, purpose="register", is_used=False)
        .order_by("-created_at")
        .first()
    )
    if latest and latest.created_at + timedelta(seconds=60) > timezone.now():
        raise BusinessError(4090, "CODE_COOLDOWN", status.HTTP_409_CONFLICT)

    code = f"{secrets.randbelow(1000000):06d}"
    _validate_smtp_settings()
    try:
        send_mail(
            "WHU Online Education Verification Code",
            f"Your verification code is {code}. It is valid for 5 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except (ImproperlyConfigured, smtplib.SMTPException, OSError):
        raise BusinessError(5000, "EMAIL_SEND_FAILED", status.HTTP_500_INTERNAL_SERVER_ERROR)

    now = timezone.now()
    with transaction.atomic():
        EmailVerificationCode.objects.filter(email=email, purpose="register", is_used=False).update(
            is_used=True,
            used_at=now,
        )
        EmailVerificationCode.objects.create(
            email=email,
            purpose="register",
            code_hash=hash_email_code(email, code),
            expires_at=now + timedelta(minutes=5),
            request_ip=request_ip,
        )

    return {"email": email, "expires_in": 300, "cooldown_seconds": 60}


def verify_register_email_code(email, code):
    email = email.strip().lower()
    record = (
        EmailVerificationCode.objects.select_for_update()
        .filter(email=email, purpose="register", is_used=False)
        .order_by("-created_at")
        .first()
    )
    if not record:
        raise BusinessError(4000, "CODE_NOT_FOUND")
    if record.expires_at < timezone.now():
        raise BusinessError(4000, "CODE_EXPIRED")
    if record.attempt_count >= 5:
        raise BusinessError(4000, "CODE_TOO_MANY_ATTEMPTS")
    if record.code_hash != hash_email_code(email, code):
        record.attempt_count += 1
        record.save(update_fields=["attempt_count"])
        raise BusinessError(4000, "CODE_INVALID")

    record.is_used = True
    record.used_at = timezone.now()
    record.save(update_fields=["is_used", "used_at"])


@transaction.atomic
def register_user(username, email, password, role, email_code):
    email = email.strip().lower()
    if User.objects.filter(username=username).exists():
        raise BusinessError(4090, "USERNAME_EXISTS", status.HTTP_409_CONFLICT)
    if User.objects.filter(email=email).exists():
        raise BusinessError(4090, "EMAIL_EXISTS", status.HTTP_409_CONFLICT)
    verify_register_email_code(email, email_code)
    user = User.objects.create_user(username=username, email=email, password=password)
    ensure_user_profile(user, role=role)
    return user
