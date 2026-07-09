from django.conf import settings
from django.db import models


TARGET_POST = "post"
TARGET_RESOURCE = "resource"
TARGET_CHOICES = (
    (TARGET_POST, "post"),
    (TARGET_RESOURCE, "resource"),
)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_posts")
    title = models.CharField(max_length=128)
    content = models.TextField()
    likes_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=["author"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return self.title


class PostAttachment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="community/post-attachments/")
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=128, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "id")
        indexes = [
            models.Index(fields=["post"]),
        ]

    def __str__(self):
        return f"{self.post_id} - {self.original_name}"


class Resource(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_resources")
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=500, blank=True)
    file = models.FileField(upload_to="community/resources/", blank=True, null=True)
    original_name = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=128, blank=True)
    size = models.PositiveBigIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=["author"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_comments")
    target_type = models.CharField(max_length=16, choices=TARGET_CHOICES)
    target_id = models.PositiveIntegerField()
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "id")
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self):
        return f"{self.target_type}:{self.target_id} - {self.author_id}"


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_likes")
    target_type = models.CharField(max_length=16, choices=TARGET_CHOICES)
    target_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "target_type", "target_id"], name="unique_like_per_user_target"),
        ]
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self):
        return f"{self.user_id} likes {self.target_type}:{self.target_id}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="community_favorites")
    target_type = models.CharField(max_length=16, choices=TARGET_CHOICES)
    target_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = [
            models.UniqueConstraint(fields=["user", "target_type", "target_id"], name="unique_favorite_per_user_target"),
        ]
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self):
        return f"{self.user_id} favorites {self.target_type}:{self.target_id}"
