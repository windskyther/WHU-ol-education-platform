from rest_framework import serializers

from apps.exams.models import Exam, ExamSubmission, Question


class ExamSerializer(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()
    submitted = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = (
            "id",
            "course",
            "title",
            "description",
            "total_score",
            "duration_minutes",
            "is_published",
            "start_time",
            "end_time",
            "question_count",
            "submitted",
            "score",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "course", "question_count", "submitted", "score", "created_at", "updated_at")

    def get_question_count(self, obj):
        if hasattr(obj, "question_count"):
            return obj.question_count
        return obj.questions.count()

    def get_submitted(self, obj):
        student = self.context.get("student")
        if not student:
            return False
        return ExamSubmission.objects.filter(exam=obj, student=student).exists()

    def get_score(self, obj):
        student = self.context.get("student")
        if not student:
            return None
        submission = ExamSubmission.objects.filter(exam=obj, student=student).first()
        return submission.score if submission else None


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "exam", "question_type", "content", "options", "answer", "score", "order", "created_at", "updated_at")
        read_only_fields = ("id", "exam", "created_at", "updated_at")

    def validate_options(self, value):
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("OPTIONS_MUST_BE_LIST")
        return value

    def validate_answer(self, value):
        if value in (None, ""):
            return []
        if isinstance(value, list):
            return value
        return [value]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get("hide_answer"):
            data.pop("answer", None)
        return data


class ExamDetailSerializer(ExamSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(ExamSerializer.Meta):
        fields = ExamSerializer.Meta.fields + ("questions",)

    def get_questions(self, obj):
        questions = obj.questions.all()
        return QuestionSerializer(
            questions,
            many=True,
            context={"hide_answer": self.context.get("hide_answer")},
        ).data


class ExamSubmitSerializer(serializers.Serializer):
    answers = serializers.DictField()

    def validate_answers(self, value):
        normalized = {}
        for key, answer in value.items():
            try:
                question_id = str(int(key))
            except (TypeError, ValueError):
                raise serializers.ValidationError("QUESTION_ID_INVALID")
            normalized[question_id] = answer if isinstance(answer, list) else [answer]
        return normalized


class ExamSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    course_id = serializers.IntegerField(source="exam.course_id", read_only=True)
    course_title = serializers.CharField(source="exam.course.title", read_only=True)

    class Meta:
        model = ExamSubmission
        fields = ("id", "exam", "exam_title", "course_id", "course_title", "student", "answers", "score", "submitted_at")
        read_only_fields = fields

    def get_student(self, obj):
        return {
            "id": obj.student.id,
            "username": obj.student.username,
            "email": obj.student.email,
        }
