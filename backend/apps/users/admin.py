from django.contrib import admin
from apps.users.models import EmailVerificationCode, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "purpose", "expires_at", "is_used", "attempt_count", "created_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("email",)
