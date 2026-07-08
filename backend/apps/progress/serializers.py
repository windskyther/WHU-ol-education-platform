from rest_framework import serializers

from apps.courses.serializers import CourseSerializer
from apps.progress.models import Enrollment, LearningProgress


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ("id", "course", "progress", "enrolled_at", "last_learned_at")
        read_only_fields = fields


class LearningProgressSerializer(serializers.ModelSerializer):
    chapter_id = serializers.IntegerField(read_only=True)
    chapter = serializers.SerializerMethodField()

    def get_chapter(self, obj):
        return {
            "id": obj.chapter_id,
            "course": obj.course_id,
            "title": obj.chapter.title,
            "description": obj.chapter.description,
            "order": obj.chapter.order,
        }

    class Meta:
        model = LearningProgress
        fields = ("id", "course", "chapter_id", "chapter", "watched_seconds", "percent", "is_completed", "updated_at")
        read_only_fields = fields


class ProgressUpdateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    chapter_id = serializers.IntegerField()
    watched_seconds = serializers.IntegerField(min_value=0)
    percent = serializers.FloatField(min_value=0, max_value=100, required=False)
    is_completed = serializers.BooleanField(required=False)


class CourseProgressSerializer(serializers.Serializer):
    course = CourseSerializer()
    enrollment = EnrollmentSerializer()
    progress_items = LearningProgressSerializer(many=True)
