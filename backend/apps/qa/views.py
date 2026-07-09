from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.exceptions import BusinessError
from apps.common.pagination import StandardPagination
from apps.common.permissions import get_user_role
from apps.common.responses import api_response
from apps.courses.models import Course
from apps.progress.models import Enrollment
from apps.qa.models import CourseAnswer, CourseQuestion
from apps.qa.serializers import CourseAnswerUpsertSerializer, CourseQuestionSerializer


def get_course_for_question(course_id):
    course = Course.objects.select_related("teacher").filter(id=course_id, is_deleted=False).first()
    if not course:
        raise BusinessError(4040, "COURSE_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    return course


def is_course_manager(user, course):
    role = get_user_role(user)
    return role == "admin" or (role == "teacher" and course.teacher_id == user.id)


def assert_question_list_access(user, course):
    role = get_user_role(user)
    if is_course_manager(user, course):
        return role
    if role == "student" and Enrollment.objects.filter(student=user, course=course).exists():
        return role
    raise BusinessError(4003, "QUESTION_ACCESS_REQUIRED", status.HTTP_403_FORBIDDEN)


def assert_student_enrolled(user, course):
    if get_user_role(user) != "student":
        raise BusinessError(4003, "ONLY_STUDENT_CAN_ASK_QUESTION", status.HTTP_403_FORBIDDEN)
    if not course.is_published:
        raise BusinessError(4040, "COURSE_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    if not Enrollment.objects.filter(student=user, course=course).exists():
        raise BusinessError(4003, "ENROLLMENT_REQUIRED", status.HTTP_403_FORBIDDEN)


def assert_course_manager(user, course):
    if not is_course_manager(user, course):
        raise BusinessError(4003, "COURSE_MANAGER_REQUIRED", status.HTTP_403_FORBIDDEN)


def get_question_for_access(question_id, user):
    question = (
        CourseQuestion.objects.select_related("course", "course__teacher", "student")
        .prefetch_related("answer")
        .filter(id=question_id, course__is_deleted=False)
        .first()
    )
    if not question:
        raise BusinessError(4040, "QUESTION_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    assert_question_list_access(user, question.course)
    return question


class CourseQuestionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_course_for_question(course_id)
        role = assert_question_list_access(request.user, course)
        queryset = (
            CourseQuestion.objects.filter(course=course)
            .select_related("student", "answer", "answer__teacher")
            .order_by("-updated_at", "-id")
        )
        if role == "student":
            queryset = queryset.filter(student=request.user)
        status_filter = request.query_params.get("status")
        if status_filter in {CourseQuestion.STATUS_OPEN, CourseQuestion.STATUS_ANSWERED, CourseQuestion.STATUS_RESOLVED}:
            queryset = queryset.filter(status=status_filter)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CourseQuestionSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def post(self, request, course_id):
        course = get_course_for_question(course_id)
        assert_student_enrolled(request.user, course)
        serializer = CourseQuestionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        question = serializer.save(course=course, student=request.user)
        return api_response(
            CourseQuestionSerializer(question, context={"request": request}).data,
            "question created",
            status=status.HTTP_201_CREATED,
        )


class CourseQuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, question_id):
        question = get_question_for_access(question_id, request.user)
        return api_response(CourseQuestionSerializer(question, context={"request": request}).data)


class CourseQuestionAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, question_id):
        question = get_question_for_access(question_id, request.user)
        assert_course_manager(request.user, question.course)
        serializer = CourseAnswerUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer, _ = CourseAnswer.objects.update_or_create(
            question=question,
            defaults={
                "teacher": request.user,
                "content": serializer.validated_data["content"],
            },
        )
        if question.status == CourseQuestion.STATUS_OPEN:
            question.status = CourseQuestion.STATUS_ANSWERED
            question.save(update_fields=["status", "updated_at"])
        answer.question = question
        return api_response(CourseQuestionSerializer(question, context={"request": request}).data, "question answered")


class CourseQuestionResolveView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, question_id):
        question = get_question_for_access(question_id, request.user)
        role = get_user_role(request.user)
        if not is_course_manager(request.user, question.course) and not (role == "student" and question.student_id == request.user.id):
            raise BusinessError(4003, "QUESTION_RESOLVE_REQUIRED", status.HTTP_403_FORBIDDEN)
        question.status = CourseQuestion.STATUS_RESOLVED
        question.resolved_at = timezone.now()
        question.save(update_fields=["status", "resolved_at", "updated_at"])
        return api_response(CourseQuestionSerializer(question, context={"request": request}).data, "question resolved")
