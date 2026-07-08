from django.contrib import admin

from apps.exams.models import Exam, ExamSubmission, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "total_score", "duration_minutes", "is_published", "created_at")
    list_filter = ("is_published", "course")
    search_fields = ("title", "course__title")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "question_type", "score", "order")
    list_filter = ("question_type", "exam")
    search_fields = ("content", "exam__title")


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "student", "score", "submitted_at")
    list_filter = ("exam",)
    search_fields = ("exam__title", "student__username", "student__email")
