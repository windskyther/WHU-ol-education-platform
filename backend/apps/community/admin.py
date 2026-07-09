from django.contrib import admin

from apps.community.models import Comment, Favorite, Like, Post, PostAttachment, Resource


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "likes_count", "favorites_count", "comments_count", "is_deleted", "created_at")
    search_fields = ("title", "content")
    list_filter = ("is_deleted",)


@admin.register(PostAttachment)
class PostAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "original_name", "size", "created_at")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "url", "likes_count", "favorites_count", "comments_count", "is_deleted", "created_at")
    search_fields = ("title", "description")
    list_filter = ("is_deleted",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "target_type", "target_id", "author", "created_at")
    list_filter = ("target_type",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "target_type", "target_id", "user", "created_at")
    list_filter = ("target_type",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "target_type", "target_id", "user", "created_at")
    list_filter = ("target_type",)
