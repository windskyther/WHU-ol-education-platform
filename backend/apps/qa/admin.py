from django.contrib import admin

from apps.qa.models import CourseAnswer, CourseQuestion


@admin.register(CourseQuestion)
class CourseQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "student", "title", "status", "updated_at")
    list_filter = ("status", "course")
    search_fields = ("title", "content", "student__username", "course__title")


@admin.register(CourseAnswer)
class CourseAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "teacher", "updated_at")
    search_fields = ("content", "question__title", "teacher__username")
