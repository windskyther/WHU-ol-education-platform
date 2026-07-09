from pathlib import Path

from rest_framework import serializers

from apps.courses.models import Chapter, Course, Material
from apps.users.models import ensure_user_profile


MAX_COVER_SIZE = 5 * 1024 * 1024
MAX_VIDEO_SIZE = 200 * 1024 * 1024
MAX_MATERIAL_SIZE = 20 * 1024 * 1024

ALLOWED_COVER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
ALLOWED_MATERIAL_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".txt", ".zip"}


def validate_file(file_obj, allowed_extensions, max_size, error_prefix):
    extension = Path(file_obj.name).suffix.lower()
    if extension not in allowed_extensions:
        raise serializers.ValidationError(f"{error_prefix}_TYPE_NOT_ALLOWED")
    if file_obj.size > max_size:
        raise serializers.ValidationError(f"{error_prefix}_SIZE_EXCEEDED")


class TeacherBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()


class MaterialSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = ("id", "kind", "url", "original_name", "content_type", "size", "created_at")
        read_only_fields = fields

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        if obj.file:
            return obj.file.url
        return None


class ChapterSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    material = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = ("id", "course", "title", "description", "order", "video", "material", "created_at", "updated_at")
        read_only_fields = ("id", "course", "video", "material", "created_at", "updated_at")

    def get_video(self, obj):
        material = obj.materials.filter(kind=Material.KIND_VIDEO).first()
        return MaterialSerializer(material, context=self.context).data if material else None

    def get_material(self, obj):
        material = obj.materials.filter(kind=Material.KIND_DOCUMENT).first()
        return MaterialSerializer(material, context=self.context).data if material else None


class CourseSerializer(serializers.ModelSerializer):
    teacher = TeacherBriefSerializer(read_only=True)
    teacher_role = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()
    chapter_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "cover",
            "cover_url",
            "category",
            "level",
            "teacher",
            "teacher_role",
            "is_published",
            "published_at",
            "chapter_count",
            "is_enrolled",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "teacher",
            "teacher_role",
            "cover_url",
            "published_at",
            "chapter_count",
            "is_enrolled",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"cover": {"write_only": True, "required": False, "allow_null": True}}

    def get_teacher_role(self, obj):
        return ensure_user_profile(obj.teacher).role

    def get_cover_url(self, obj):
        request = self.context.get("request")
        if obj.cover and request:
            return request.build_absolute_uri(obj.cover.url)
        if obj.cover:
            return obj.cover.url
        return None

    def get_chapter_count(self, obj):
        if hasattr(obj, "chapter_count"):
            return obj.chapter_count
        return obj.chapters.count()

    def get_is_enrolled(self, obj):
        if hasattr(obj, "is_enrolled"):
            return bool(obj.is_enrolled)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or ensure_user_profile(user).role != "student":
            return False
        from apps.progress.models import Enrollment

        return Enrollment.objects.filter(student=user, course=obj).exists()

    def validate_cover(self, value):
        if value:
            validate_file(value, ALLOWED_COVER_EXTENSIONS, MAX_COVER_SIZE, "COVER")
        return value


class CoursePublishSerializer(serializers.Serializer):
    is_published = serializers.BooleanField(default=True)


class UploadMaterialSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        kind = self.context["kind"]
        if kind == Material.KIND_VIDEO:
            validate_file(value, ALLOWED_VIDEO_EXTENSIONS, MAX_VIDEO_SIZE, "VIDEO")
        else:
            validate_file(value, ALLOWED_MATERIAL_EXTENSIONS, MAX_MATERIAL_SIZE, "MATERIAL")
        return value
