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
from apps.courses.models import Chapter, Course
from apps.progress.models import Enrollment, LearningProgress
from apps.progress.serializers import EnrollmentSerializer, LearningProgressSerializer, ProgressUpdateSerializer


def assert_student(user):
    if not user or not user.is_authenticated:
        raise BusinessError(4001, "AUTHENTICATION_REQUIRED", status.HTTP_401_UNAUTHORIZED)
    if get_user_role(user) != "student":
        raise BusinessError(4003, "ONLY_STUDENT_CAN_ENROLL", status.HTTP_403_FORBIDDEN)


def get_visible_published_course(course_id):
    course = Course.objects.filter(id=course_id, is_deleted=False, is_published=True).first()
    if not course:
        raise BusinessError(4040, "COURSE_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    return course


def get_enrollment(student, course):
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if not enrollment:
        raise BusinessError(4003, "ENROLLMENT_REQUIRED", status.HTTP_403_FORBIDDEN)
    return enrollment


def sync_enrollment_progress(enrollment):
    total_chapters = Chapter.objects.filter(course=enrollment.course).count()
    if total_chapters == 0:
        progress = 0
    else:
        progress_items = LearningProgress.objects.filter(
            student=enrollment.student,
            course=enrollment.course,
        )
        watched_percent = sum(100 if item.is_completed else item.percent for item in progress_items)
        progress = round(watched_percent / total_chapters, 2)
    enrollment.progress = progress
    enrollment.last_learned_at = timezone.now()
    enrollment.save(update_fields=["progress", "last_learned_at"])
    return enrollment


class CourseEnrollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        assert_student(request.user)
        course = get_visible_published_course(course_id)
        try:
            enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        except IntegrityError:
            raise BusinessError(4090, "ALREADY_ENROLLED", status.HTTP_409_CONFLICT)
        if not created:
            raise BusinessError(4090, "ALREADY_ENROLLED", status.HTTP_409_CONFLICT)
        return api_response(
            EnrollmentSerializer(enrollment, context={"request": request}).data,
            "enrolled",
            status=status.HTTP_201_CREATED,
        )


class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assert_student(request.user)
        queryset = (
            Enrollment.objects.filter(student=request.user, course__is_deleted=False)
            .select_related("course", "course__teacher")
            .annotate(chapter_count=Count("course__chapters"))
            .order_by("-enrolled_at", "-id")
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = EnrollmentSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class ProgressUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        assert_student(request.user)
        serializer = ProgressUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chapter = (
            Chapter.objects.select_related("course")
            .filter(id=serializer.validated_data["chapter_id"], course__is_deleted=False, course__is_published=True)
            .first()
        )
        if not chapter:
            raise BusinessError(4040, "CHAPTER_NOT_FOUND", status.HTTP_404_NOT_FOUND)

        course_id = serializer.validated_data.get("course_id")
        if course_id is not None and course_id != chapter.course_id:
            raise BusinessError(4000, "CHAPTER_NOT_IN_COURSE")

        enrollment = get_enrollment(request.user, chapter.course)
        progress, _ = LearningProgress.objects.select_for_update().get_or_create(
            student=request.user,
            course=chapter.course,
            chapter=chapter,
        )
        incoming_seconds = serializer.validated_data["watched_seconds"]
        if incoming_seconds > progress.watched_seconds:
            progress.watched_seconds = incoming_seconds
        incoming_percent = serializer.validated_data.get("percent")
        if incoming_percent is not None and incoming_percent > progress.percent:
            progress.percent = incoming_percent
        if serializer.validated_data.get("is_completed") is True:
            progress.is_completed = True
        if progress.is_completed:
            progress.percent = 100
        progress.save(update_fields=["watched_seconds", "percent", "is_completed", "updated_at"])
        enrollment = sync_enrollment_progress(enrollment)
        progress_data = LearningProgressSerializer(progress, context={"request": request}).data
        return api_response(
            {
                "progress": enrollment.progress,
                "enrollment": EnrollmentSerializer(enrollment, context={"request": request}).data,
                "progress_item": progress_data,
                "chapter_progress": [progress_data],
            },
            "progress updated",
        )


class CourseProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = Course.objects.filter(id=course_id, is_deleted=False).select_related("teacher").first()
        if not course:
            raise BusinessError(4040, "COURSE_NOT_FOUND", status.HTTP_404_NOT_FOUND)

        role = get_user_role(request.user)
        if role == "student":
            enrollment = get_enrollment(request.user, course)
            progress_items = LearningProgress.objects.filter(student=request.user, course=course).select_related(
                "course",
                "chapter",
            )
            data = {
                "course_id": course.id,
                "student_id": request.user.id,
                "progress": enrollment.progress,
                "enrollment": EnrollmentSerializer(enrollment, context={"request": request}).data,
                "progress_items": LearningProgressSerializer(progress_items, many=True, context={"request": request}).data,
            }
            data["chapter_progress"] = data["progress_items"]
            return api_response(data)

        if role in {"teacher", "admin"}:
            if role != "admin" and course.teacher_id != request.user.id:
                raise BusinessError(4003, "COURSE_OWNER_REQUIRED", status.HTTP_403_FORBIDDEN)
            enrollments = Enrollment.objects.filter(course=course).select_related("student").order_by("-enrolled_at", "-id")
            data = {
                "course_id": course.id,
                "course_title": course.title,
                "student_count": enrollments.count(),
                "students": [
                    {
                        "student": {
                            "id": enrollment.student.id,
                            "username": enrollment.student.username,
                            "email": enrollment.student.email,
                        },
                        "progress": enrollment.progress,
                        "enrolled_at": enrollment.enrolled_at,
                        "last_learned_at": enrollment.last_learned_at,
                    }
                    for enrollment in enrollments
                ],
            }
            return api_response(data)

        raise BusinessError(4003, "PERMISSION_DENIED", status.HTTP_403_FORBIDDEN)
