from rest_framework import serializers

from apps.courses.serializers import ChapterSerializer, CourseSerializer
from apps.progress.models import Enrollment, LearningProgress


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ("id", "course", "progress", "enrolled_at", "last_learned_at")
        read_only_fields = fields


class LearningProgressSerializer(serializers.ModelSerializer):
    chapter = ChapterSerializer(read_only=True)

    class Meta:
        model = LearningProgress
        fields = ("id", "course", "chapter", "watched_seconds", "is_completed", "updated_at")
        read_only_fields = fields


class ProgressUpdateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False)
    chapter_id = serializers.IntegerField()
    watched_seconds = serializers.IntegerField(min_value=0)
    is_completed = serializers.BooleanField(required=False)


class CourseProgressSerializer(serializers.Serializer):
    course = CourseSerializer()
    enrollment = EnrollmentSerializer()
    progress_items = LearningProgressSerializer(many=True)
