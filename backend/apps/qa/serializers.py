from rest_framework import serializers

from apps.qa.models import CourseAnswer, CourseQuestion


class UserBriefSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()


class CourseAnswerSerializer(serializers.ModelSerializer):
    teacher = UserBriefSerializer(read_only=True)

    class Meta:
        model = CourseAnswer
        fields = ("id", "teacher", "content", "created_at", "updated_at")
        read_only_fields = ("id", "teacher", "created_at", "updated_at")


class CourseQuestionSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)
    answer = CourseAnswerSerializer(read_only=True)

    class Meta:
        model = CourseQuestion
        fields = (
            "id",
            "course",
            "student",
            "title",
            "content",
            "status",
            "answer",
            "resolved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "course", "student", "status", "answer", "resolved_at", "created_at", "updated_at")

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("QUESTION_TITLE_REQUIRED")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("QUESTION_CONTENT_REQUIRED")
        return value


class CourseAnswerUpsertSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=2000)

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("ANSWER_CONTENT_REQUIRED")
        return value
