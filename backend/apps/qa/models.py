from django.conf import settings
from django.db import models

from apps.courses.models import Course


class CourseQuestion(models.Model):
    STATUS_OPEN = "open"
    STATUS_ANSWERED = "answered"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = (
        (STATUS_OPEN, "open"),
        (STATUS_ANSWERED, "answered"),
        (STATUS_RESOLVED, "resolved"),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_questions")
    title = models.CharField(max_length=128)
    content = models.TextField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-id")
        indexes = [
            models.Index(fields=["course", "status"]),
            models.Index(fields=["student", "course"]),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseAnswer(models.Model):
    question = models.OneToOneField(CourseQuestion, on_delete=models.CASCADE, related_name="answer")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_answers")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-id")
        indexes = [
            models.Index(fields=["teacher"]),
        ]

    def __str__(self):
        return f"Answer for {self.question_id}"
