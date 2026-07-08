from django.contrib import admin

from apps.progress.models import Enrollment, LearningProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "progress", "enrolled_at", "last_learned_at")
    list_filter = ("course",)
    search_fields = ("student__username", "student__email", "course__title")


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "course", "chapter", "watched_seconds", "is_completed", "updated_at")
    list_filter = ("course", "is_completed")
    search_fields = ("student__username", "student__email", "course__title", "chapter__title")
