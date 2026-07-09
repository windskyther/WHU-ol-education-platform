from rest_framework import serializers

from apps.certificates.models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.username", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = (
            "id",
            "cert_no",
            "student",
            "student_name",
            "course",
            "course_title",
            "exam",
            "exam_title",
            "teacher_name",
            "score",
            "excellent_score",
            "status",
            "issued_at",
        )
        read_only_fields = fields

    def get_teacher_name(self, obj):
        teacher = obj.course.teacher
        return teacher.username if teacher else ""
