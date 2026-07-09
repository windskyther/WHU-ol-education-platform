from django.db import IntegrityError, transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.exceptions import BusinessError
from apps.common.pagination import StandardPagination
from apps.common.permissions import get_user_role
from apps.common.responses import api_response
from apps.courses.models import Course
from apps.exams.models import Exam, ExamSubmission, Question
from apps.exams.serializers import (
    ExamDetailSerializer,
    ExamSerializer,
    ExamSubmissionSerializer,
    ExamSubmitSerializer,
    QuestionSerializer,
)
from apps.progress.models import Enrollment


def is_teacher_or_admin(user):
    return get_user_role(user) in {"teacher", "admin"}


def assert_student(user):
    if not user or not user.is_authenticated:
        raise BusinessError(4001, "AUTHENTICATION_REQUIRED", status.HTTP_401_UNAUTHORIZED)
    if get_user_role(user) != "student":
        raise BusinessError(4003, "ONLY_STUDENT_CAN_SUBMIT_EXAM", status.HTTP_403_FORBIDDEN)


def assert_course_owner(user, course):
    if not user or not user.is_authenticated:
        raise BusinessError(4001, "AUTHENTICATION_REQUIRED", status.HTTP_401_UNAUTHORIZED)
    if not is_teacher_or_admin(user):
        raise BusinessError(4003, "ONLY_TEACHER_CAN_MANAGE_EXAM", status.HTTP_403_FORBIDDEN)
    if get_user_role(user) != "admin" and course.teacher_id != user.id:
        raise BusinessError(4003, "COURSE_OWNER_REQUIRED", status.HTTP_403_FORBIDDEN)


def get_course(course_id):
    course = Course.objects.filter(id=course_id, is_deleted=False).select_related("teacher").first()
    if not course:
        raise BusinessError(4040, "COURSE_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    return course


def assert_exam_read_access(user, exam):
    role = get_user_role(user) if user and user.is_authenticated else None
    if role == "admin" or exam.course.teacher_id == getattr(user, "id", None):
        return
    if not exam.is_published or not exam.course.is_published:
        raise BusinessError(4040, "EXAM_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    assert_student(user)
    if not Enrollment.objects.filter(student=user, course=exam.course).exists():
        raise BusinessError(4003, "ENROLLMENT_REQUIRED", status.HTTP_403_FORBIDDEN)


def get_exam_for_read(exam_id, user):
    exam = Exam.objects.select_related("course", "course__teacher").prefetch_related("questions").filter(
        id=exam_id,
        course__is_deleted=False,
    ).first()
    if not exam:
        raise BusinessError(4040, "EXAM_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    assert_exam_read_access(user, exam)
    return exam


def assert_student_can_enter_exam(user, exam):
    if get_user_role(user) != "student":
        return
    if ExamSubmission.objects.filter(exam=exam, student=user).exists():
        raise BusinessError(4090, "EXAM_ALREADY_SUBMITTED", status.HTTP_409_CONFLICT)
    if exam.end_time and timezone.now() >= exam.end_time:
        raise BusinessError(4000, "EXAM_ENDED", status.HTTP_400_BAD_REQUEST)


def get_question_for_write(question_id, user):
    question = Question.objects.select_related("exam", "exam__course", "exam__course__teacher").filter(
        id=question_id,
        exam__course__is_deleted=False,
    ).first()
    if not question:
        raise BusinessError(4040, "QUESTION_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    assert_course_owner(user, question.exam.course)
    return question


def normalize_answer(value):
    if isinstance(value, list):
        items = value
    else:
        items = [value]
    normalized = []
    for item in items:
        text = str(item).strip()
        if text == "":
            continue
        normalized.append(normalize_answer_text(text))
    return sorted(normalized)


def normalize_answer_text(text):
    cleaned = text.strip()
    upper = cleaned.upper()
    truthy = {"TRUE", "T", "YES", "Y", "正确", "对", "是"}
    falsy = {"FALSE", "F", "NO", "N", "错误", "错", "否"}
    if upper in truthy:
        return "true"
    if upper in falsy:
        return "false"
    if len(cleaned) >= 2 and cleaned[0].isalnum() and cleaned[1] in {".", "．", "、", ":", "：", ")", "）"}:
        return cleaned[0].upper()
    return cleaned


def calculate_score(exam, submitted_answers):
    total = 0
    details = {}
    for question in exam.questions.all():
        expected = normalize_answer(question.answer)
        actual = normalize_answer(submitted_answers.get(str(question.id), []))
        is_correct = actual == expected
        earned = float(question.score) if is_correct else 0
        total += earned
        details[str(question.id)] = {
            "answer": actual,
            "is_correct": is_correct,
            "score": earned,
        }
    return total, details


class CourseExamListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_course(course_id)
        role = get_user_role(request.user)
        if role in {"teacher", "admin"}:
            if role != "admin" and course.teacher_id != request.user.id:
                raise BusinessError(4003, "COURSE_OWNER_REQUIRED", status.HTTP_403_FORBIDDEN)
            queryset = course.exams.annotate(question_count=Count("questions")).order_by("-created_at", "-id")
            context = {"request": request}
        else:
            assert_student(request.user)
            if not course.is_published:
                raise BusinessError(4040, "COURSE_NOT_FOUND", status.HTTP_404_NOT_FOUND)
            if not Enrollment.objects.filter(student=request.user, course=course).exists():
                raise BusinessError(4003, "ENROLLMENT_REQUIRED", status.HTTP_403_FORBIDDEN)
            queryset = course.exams.filter(is_published=True).annotate(question_count=Count("questions")).order_by("-created_at", "-id")
            context = {"request": request, "student": request.user}

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ExamSerializer(page, many=True, context=context)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, course_id):
        course = get_course(course_id)
        assert_course_owner(request.user, course)
        serializer = ExamSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        exam = serializer.save(course=course)
        return api_response(ExamSerializer(exam, context={"request": request}).data, "exam created", status=status.HTTP_201_CREATED)


class ExamDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        exam = get_exam_for_read(exam_id, request.user)
        assert_student_can_enter_exam(request.user, exam)
        role = get_user_role(request.user)
        hide_answer = role == "student"
        context = {"request": request, "hide_answer": hide_answer}
        if role == "student":
            context["student"] = request.user
        return api_response(ExamDetailSerializer(exam, context=context).data)

    def put(self, request, exam_id):
        exam = get_exam_for_read(exam_id, request.user)
        assert_course_owner(request.user, exam.course)
        serializer = ExamSerializer(exam, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        exam = serializer.save()
        return api_response(ExamSerializer(exam, context={"request": request}).data, "exam updated")

    def patch(self, request, exam_id):
        return self.put(request, exam_id)

    def delete(self, request, exam_id):
        exam = get_exam_for_read(exam_id, request.user)
        assert_course_owner(request.user, exam.course)
        exam.delete()
        return api_response(None, "exam deleted")


class ExamQuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        exam = get_exam_for_read(exam_id, request.user)
        assert_student_can_enter_exam(request.user, exam)
        role = get_user_role(request.user)
        questions = exam.questions.all()
        serializer = QuestionSerializer(
            questions,
            many=True,
            context={"request": request, "hide_answer": role == "student"},
        )
        return api_response(serializer.data)

    def post(self, request, exam_id):
        exam = get_exam_for_read(exam_id, request.user)
        assert_course_owner(request.user, exam.course)
        serializer = QuestionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            question = serializer.save(exam=exam)
        except IntegrityError:
            raise BusinessError(4090, "QUESTION_ORDER_EXISTS", status.HTTP_409_CONFLICT)
        return api_response(QuestionSerializer(question, context={"request": request}).data, "question created", status=status.HTTP_201_CREATED)


class QuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, question_id):
        question = get_question_for_write(question_id, request.user)
        serializer = QuestionSerializer(question, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            question = serializer.save()
        except IntegrityError:
            raise BusinessError(4090, "QUESTION_ORDER_EXISTS", status.HTTP_409_CONFLICT)
        return api_response(QuestionSerializer(question, context={"request": request}).data, "question updated")

    def patch(self, request, question_id):
        return self.put(request, question_id)

    def delete(self, request, question_id):
        question = get_question_for_write(question_id, request.user)
        question.delete()
        return api_response(None, "question deleted")


class ExamSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, exam_id):
        assert_student(request.user)
        exam = get_exam_for_read(exam_id, request.user)
        if exam.start_time and timezone.now() < exam.start_time:
            raise BusinessError(4000, "EXAM_NOT_STARTED")
        if exam.end_time and timezone.now() > exam.end_time:
            raise BusinessError(4000, "EXAM_ENDED")

        serializer = ExamSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if ExamSubmission.objects.select_for_update().filter(exam=exam, student=request.user).exists():
            raise BusinessError(4090, "EXAM_ALREADY_SUBMITTED", status.HTTP_409_CONFLICT)

        score, answer_details = calculate_score(exam, serializer.validated_data["answers"])
        submission = ExamSubmission.objects.create(
            exam=exam,
            student=request.user,
            answers=answer_details,
            score=score,
        )
        return api_response(ExamSubmissionSerializer(submission, context={"request": request}).data, "exam submitted", status=status.HTTP_201_CREATED)


class MyScoresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assert_student(request.user)
        queryset = ExamSubmission.objects.filter(student=request.user).select_related("exam", "exam__course").order_by("-submitted_at", "-id")
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ExamSubmissionSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class ExamSubmissionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, exam_id):
        exam = get_exam_for_read(exam_id, request.user)
        assert_course_owner(request.user, exam.course)
        queryset = exam.submissions.select_related("student", "exam", "exam__course").order_by("-submitted_at", "-id")
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ExamSubmissionSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)
