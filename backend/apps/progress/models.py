from django.conf import settings
from django.db import models

from apps.courses.models import Chapter, Course


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    progress = models.FloatField(default=0)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_learned_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ("-enrolled_at",)
        constraints = [
            models.UniqueConstraint(fields=["student", "course"], name="unique_enrollment_student_course"),
        ]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"{self.student} -> {self.course}"


class LearningProgress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learning_progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="learning_progress")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="learning_progress")
    watched_seconds = models.PositiveIntegerField(default=0)
    percent = models.FloatField(default=0)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("chapter__order", "chapter_id")
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course", "chapter"],
                name="unique_learning_progress_student_course_chapter",
            ),
        ]
        indexes = [
            models.Index(fields=["student", "course"]),
            models.Index(fields=["chapter"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.chapter}: {self.watched_seconds}s"
