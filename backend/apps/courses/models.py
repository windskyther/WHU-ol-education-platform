from django.conf import settings
from django.db import models


class Course(models.Model):
    LEVEL_BEGINNER = "beginner"
    LEVEL_INTERMEDIATE = "intermediate"
    LEVEL_ADVANCED = "advanced"
    LEVEL_CHOICES = (
        (LEVEL_BEGINNER, "beginner"),
        (LEVEL_INTERMEDIATE, "intermediate"),
        (LEVEL_ADVANCED, "advanced"),
    )

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)
    category = models.CharField(max_length=64, blank=True)
    level = models.CharField(max_length=32, choices=LEVEL_CHOICES, default=LEVEL_BEGINNER)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teaching_courses")
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["teacher"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return self.title


class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("order", "id")
        constraints = [
            models.UniqueConstraint(fields=["course", "order"], name="unique_chapter_order_per_course"),
        ]
        indexes = [
            models.Index(fields=["course"]),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Material(models.Model):
    KIND_VIDEO = "video"
    KIND_DOCUMENT = "material"
    KIND_CHOICES = (
        (KIND_VIDEO, "video"),
        (KIND_DOCUMENT, "material"),
    )

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="materials")
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    file = models.FileField(upload_to="materials/")
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=128, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("kind", "-created_at")
        constraints = [
            models.UniqueConstraint(fields=["chapter", "kind"], name="unique_material_kind_per_chapter"),
        ]
        indexes = [
            models.Index(fields=["chapter"]),
            models.Index(fields=["kind"]),
        ]

    def __str__(self):
        return f"{self.chapter.title} - {self.kind}"
