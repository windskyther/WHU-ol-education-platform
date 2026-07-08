from django.contrib import admin

from apps.courses.models import Chapter, Course, Material


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "teacher", "category", "level", "is_published", "is_deleted", "created_at")
    list_filter = ("is_published", "is_deleted", "level", "category")
    search_fields = ("title", "description", "teacher__username", "teacher__email")
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order", "created_at")
    list_filter = ("course",)
    search_fields = ("title", "description", "course__title")


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "chapter", "kind", "original_name", "size", "created_at")
    list_filter = ("kind",)
    search_fields = ("original_name", "chapter__title", "chapter__course__title")
