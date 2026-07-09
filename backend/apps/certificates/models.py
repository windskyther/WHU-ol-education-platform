import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.courses.models import Course
from apps.exams.models import Exam


def generate_cert_no():
    year = timezone.now().year
    while True:
        candidate = f"CERT-{year}-{secrets.token_hex(4).upper()}"
        if not Certificate.objects.filter(cert_no=candidate).exists():
            return candidate


class Certificate(models.Model):
    STATUS_VALID = "valid"
    STATUS_REVOKED = "revoked"
    STATUS_CHOICES = (
        (STATUS_VALID, "valid"),
        (STATUS_REVOKED, "revoked"),
    )

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="certificates")
    cert_no = models.CharField(max_length=32, unique=True, editable=False)
    score = models.FloatField()
    excellent_score = models.FloatField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_VALID)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-issued_at", "-id")
        constraints = [
            models.UniqueConstraint(fields=["student", "exam"], name="unique_certificate_student_exam"),
        ]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["course"]),
            models.Index(fields=["cert_no"]),
        ]

    def save(self, *args, **kwargs):
        if not self.cert_no:
            self.cert_no = generate_cert_no()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cert_no} - {self.student} - {self.course}"
