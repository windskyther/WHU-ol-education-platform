from rest_framework import serializers
from django.utils import timezone

from apps.exams.models import Exam, ExamSubmission, Question


class ExamSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    pass_score = serializers.SerializerMethodField()
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
            "pass_score",
            "duration_minutes",
            "duration",
            "is_published",
            "start_time",
            "end_time",
            "question_count",
            "submitted",
            "score",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "course", "pass_score", "duration", "question_count", "submitted", "score", "created_at", "updated_at")

    def to_internal_value(self, data):
        data = data.copy()
        if "duration_minutes" not in data and "duration" in data:
            data["duration_minutes"] = data.get("duration")
        if "total_score" not in data:
            if "totalScore" in data:
                data["total_score"] = data.get("totalScore")
            elif "pass_score" in data:
                data["total_score"] = data.get("pass_score")
        if "is_published" not in data:
            if "isPublished" in data:
                data["is_published"] = data.get("isPublished")
            elif "published" in data:
                data["is_published"] = data.get("published")
        for field in ("start_time", "end_time"):
            if data.get(field) == "":
                data[field] = None
        return super().to_internal_value(data)

    def get_duration(self, obj):
        return obj.duration_minutes

    def get_pass_score(self, obj):
        return obj.total_score

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

    def validate(self, attrs):
        now = timezone.now()
        for field in ("start_time", "end_time"):
            value = attrs.get(field)
            if value and value <= now:
                raise serializers.ValidationError({field: f"{field.upper()}_MUST_BE_FUTURE"})

        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({"end_time": "END_TIME_MUST_BE_AFTER_START_TIME"})
        return attrs


class QuestionSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    order_no = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "id",
            "exam",
            "question_type",
            "type",
            "content",
            "options",
            "answer",
            "score",
            "order",
            "order_no",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "exam", "type", "order_no", "created_at", "updated_at")

    def to_internal_value(self, data):
        data = data.copy()
        if "question_type" not in data and "type" in data:
            data["question_type"] = self.normalize_question_type(data.get("type"))
        elif "question_type" in data:
            data["question_type"] = self.normalize_question_type(data.get("question_type"))
        if "order" not in data and "order_no" in data:
            data["order"] = data.get("order_no")
        data.pop("analysis", None)
        return super().to_internal_value(data)

    def normalize_question_type(self, value):
        aliases = {
            "judge": Question.TYPE_TRUE_FALSE,
            "truefalse": Question.TYPE_TRUE_FALSE,
            "true_false": Question.TYPE_TRUE_FALSE,
            "blank": Question.TYPE_FILL,
            "fill_blank": Question.TYPE_FILL,
            "short": Question.TYPE_FILL,
        }
        return aliases.get(value, value)

    def get_type(self, obj):
        aliases = {
            Question.TYPE_TRUE_FALSE: "judge",
            Question.TYPE_FILL: "blank",
        }
        return aliases.get(obj.question_type, obj.question_type)

    def get_order_no(self, obj):
        return obj.order

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
    answers = serializers.JSONField()

    def validate_answers(self, value):
        normalized = {}
        if isinstance(value, list):
            items = []
            for item in value:
                if not isinstance(item, dict):
                    raise serializers.ValidationError("ANSWER_ITEM_INVALID")
                question_id = item.get("question_id", item.get("id"))
                answer = item.get("answer", item.get("value", item.get("answers", [])))
                items.append((question_id, answer))
        elif isinstance(value, dict):
            items = value.items()
        else:
            raise serializers.ValidationError("ANSWERS_MUST_BE_OBJECT_OR_LIST")

        for key, answer in items:
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
    total_score = serializers.SerializerMethodField()
    objective_score = serializers.SerializerMethodField()
    subjective_score = serializers.SerializerMethodField()
    pass_score = serializers.IntegerField(source="exam.total_score", read_only=True)
    status = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()

    class Meta:
        model = ExamSubmission
        fields = (
            "id",
            "exam",
            "exam_title",
            "course_id",
            "course_title",
            "student",
            "answers",
            "score",
            "total_score",
            "objective_score",
            "subjective_score",
            "pass_score",
            "status",
            "passed",
            "submitted_at",
        )
        read_only_fields = fields

    def get_student(self, obj):
        return {
            "id": obj.student.id,
            "username": obj.student.username,
            "email": obj.student.email,
        }

    def get_total_score(self, obj):
        return obj.score

    def get_objective_score(self, obj):
        return obj.score

    def get_subjective_score(self, obj):
        return 0

    def get_status(self, obj):
        return "submitted"

    def get_passed(self, obj):
        return obj.score >= obj.exam.total_score
