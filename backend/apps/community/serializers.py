from pathlib import Path

from rest_framework import serializers

from apps.community.models import (
    POST_CATEGORY_CHOICES,
    RESOURCE_CATEGORY_CHOICES,
    TARGET_POST,
    TARGET_RESOURCE,
    Comment,
    Favorite,
    Like,
    Post,
    PostAttachment,
    Resource,
)
from apps.users.models import ensure_user_profile

POST_CATEGORY_LABELS = dict(POST_CATEGORY_CHOICES)
RESOURCE_CATEGORY_LABELS = dict(RESOURCE_CATEGORY_CHOICES)

MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024
MAX_RESOURCE_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".txt",
    ".zip",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def validate_upload_file(file_obj, error_prefix):
    extension = Path(file_obj.name).suffix.lower()
    if extension not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise serializers.ValidationError(f"{error_prefix}_TYPE_NOT_ALLOWED")
    if file_obj.size > MAX_ATTACHMENT_SIZE:
        raise serializers.ValidationError(f"{error_prefix}_SIZE_EXCEEDED")


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def is_image_file(content_type, name):
    if content_type and content_type.startswith("image/"):
        return True
    if name and Path(name).suffix.lower() in IMAGE_EXTENSIONS:
        return True
    return False


class UserBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    def get_role(self, obj):
        return ensure_user_profile(obj).role

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        profile = ensure_user_profile(obj)
        if profile.avatar and request:
            return request.build_absolute_uri(profile.avatar.url)
        if profile.avatar:
            return profile.avatar.url
        return None


class PostAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    is_image = serializers.SerializerMethodField()

    class Meta:
        model = PostAttachment
        fields = ("id", "url", "original_name", "content_type", "size", "is_image", "created_at")
        read_only_fields = fields

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return None

    def get_is_image(self, obj):
        return is_image_file(obj.content_type, obj.original_name)


class PostSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    category_label = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "category",
            "category_label",
            "attachments",
            "likes_count",
            "favorites_count",
            "comments_count",
            "is_liked",
            "is_favorited",
            "is_mine",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author",
            "category_label",
            "attachments",
            "likes_count",
            "favorites_count",
            "comments_count",
            "is_liked",
            "is_favorited",
            "is_mine",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"category": {"required": False, "allow_blank": True}}

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("POST_TITLE_REQUIRED")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("POST_CONTENT_REQUIRED")
        return value

    def get_category_label(self, obj):
        return POST_CATEGORY_LABELS.get(obj.category, "")

    def get_is_liked(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Like.objects.filter(user=user, target_type=TARGET_POST, target_id=obj.id).exists()

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, target_type=TARGET_POST, target_id=obj.id).exists()

    def get_is_mine(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and obj.author_id == user.id)


class ResourceSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()
    is_image = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = (
            "id",
            "author",
            "title",
            "description",
            "category",
            "category_label",
            "url",
            "file",
            "file_url",
            "original_name",
            "content_type",
            "size",
            "is_image",
            "likes_count",
            "favorites_count",
            "comments_count",
            "is_liked",
            "is_favorited",
            "is_mine",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author",
            "category_label",
            "file_url",
            "original_name",
            "content_type",
            "size",
            "is_image",
            "likes_count",
            "favorites_count",
            "comments_count",
            "is_liked",
            "is_favorited",
            "is_mine",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {
            "file": {"write_only": True, "required": False, "allow_null": True},
            "category": {"required": False, "allow_blank": True},
        }

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("RESOURCE_TITLE_REQUIRED")
        return value

    def validate_file(self, value):
        if value:
            validate_upload_file(value, "RESOURCE_FILE")
        return value

    def validate(self, attrs):
        url = attrs.get("url") or (self.instance.url if self.instance else "")
        file_obj = attrs.get("file") if "file" in attrs else (self.instance.file if self.instance else None)
        if not url and not file_obj:
            raise serializers.ValidationError("RESOURCE_URL_OR_FILE_REQUIRED")
        return attrs

    def create(self, validated_data):
        file_obj = validated_data.get("file")
        if file_obj:
            validated_data["original_name"] = file_obj.name
            validated_data["content_type"] = getattr(file_obj, "content_type", "") or ""
            validated_data["size"] = file_obj.size
        return super().create(validated_data)

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return None

    def get_category_label(self, obj):
        return RESOURCE_CATEGORY_LABELS.get(obj.category, "")

    def get_is_image(self, obj):
        if not obj.file:
            return False
        return is_image_file(obj.content_type, obj.original_name)

    def get_is_liked(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Like.objects.filter(user=user, target_type=TARGET_RESOURCE, target_id=obj.id).exists()

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, target_type=TARGET_RESOURCE, target_id=obj.id).exists()

    def get_is_mine(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and obj.author_id == user.id)


class CommentSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "target_type", "target_id", "author", "content", "created_at")
        read_only_fields = ("id", "target_type", "target_id", "author", "created_at")

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("COMMENT_CONTENT_REQUIRED")
        return value


class PostAttachmentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        validate_upload_file(value, "ATTACHMENT")
        return value
