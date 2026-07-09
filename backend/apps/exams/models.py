from django.conf import settings
from django.db import models

from apps.courses.models import Course


class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    total_score = models.PositiveIntegerField(default=100)
    excellent_score = models.FloatField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_published = models.BooleanField(default=False)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=["course"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["start_time", "end_time"]),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    TYPE_SINGLE = "single"
    TYPE_MULTIPLE = "multiple"
    TYPE_TRUE_FALSE = "true_false"
    TYPE_FILL = "fill"
    TYPE_CHOICES = (
        (TYPE_SINGLE, "single"),
        (TYPE_MULTIPLE, "multiple"),
        (TYPE_TRUE_FALSE, "true_false"),
        (TYPE_FILL, "fill"),
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TYPE_SINGLE)
    content = models.TextField()
    options = models.JSONField(default=list, blank=True)
    answer = models.JSONField(default=list)
    score = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "id")
        constraints = [
            models.UniqueConstraint(fields=["exam", "order"], name="unique_question_order_per_exam"),
        ]
        indexes = [
            models.Index(fields=["exam"]),
            models.Index(fields=["question_type"]),
        ]

    def __str__(self):
        return f"{self.exam.title} - Q{self.order}"


class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exam_submissions")
    answers = models.JSONField(default=dict)
    score = models.FloatField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-submitted_at", "-id")
        constraints = [
            models.UniqueConstraint(fields=["exam", "student"], name="unique_exam_submission_student"),
        ]
        indexes = [
            models.Index(fields=["exam"]),
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"{self.student} -> {self.exam}: {self.score}"
