from urllib.parse import quote

from django.db import IntegrityError
from django.http import FileResponse
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.common.exceptions import BusinessError
from apps.common.pagination import StandardPagination
from apps.common.permissions import get_user_role
from apps.common.responses import api_response
from apps.courses.models import Chapter, Course, Material
from apps.courses.serializers import (
    ChapterSerializer,
    CoursePublishSerializer,
    CourseSerializer,
    MaterialSerializer,
    UploadMaterialSerializer,
)


def annotate_enrollment_state(queryset, user):
    role = get_user_role(user) if user and user.is_authenticated else None
    if role != "student":
        return queryset.annotate(is_enrolled=Value(False, output_field=BooleanField()))
    from apps.progress.models import Enrollment

    return queryset.annotate(
        is_enrolled=Exists(
            Enrollment.objects.filter(student=user, course_id=OuterRef("pk")),
        ),
    )


def is_teacher_or_admin(user):
    return get_user_role(user) in {"teacher", "admin"}


def assert_teacher_or_admin(user):
    if not user or not user.is_authenticated:
        raise BusinessError(4001, "AUTHENTICATION_REQUIRED", status.HTTP_401_UNAUTHORIZED)
    if not is_teacher_or_admin(user):
        raise BusinessError(4003, "ONLY_TEACHER_CAN_MANAGE_COURSE", status.HTTP_403_FORBIDDEN)


def assert_course_owner(user, course):
    assert_teacher_or_admin(user)
    if get_user_role(user) != "admin" and course.teacher_id != user.id:
        raise BusinessError(4003, "COURSE_OWNER_REQUIRED", status.HTTP_403_FORBIDDEN)


def get_course_for_read(course_id, user):
    queryset = Course.objects.filter(id=course_id, is_deleted=False).annotate(chapter_count=Count("chapters"))
    queryset = annotate_enrollment_state(queryset, user)
    course = queryset.first()
    if not course:
        raise BusinessError(4040, "COURSE_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    if course.is_published:
        return course
    if user and user.is_authenticated and (get_user_role(user) == "admin" or course.teacher_id == user.id):
        return course
    raise BusinessError(4040, "COURSE_NOT_FOUND", status.HTTP_404_NOT_FOUND)


def get_chapter_for_write(chapter_id, user):
    chapter = Chapter.objects.select_related("course", "course__teacher").filter(id=chapter_id, course__is_deleted=False).first()
    if not chapter:
        raise BusinessError(4040, "CHAPTER_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    assert_course_owner(user, chapter.course)
    return chapter


def assert_chapter_read_access(user, course):
    if user and user.is_authenticated and (get_user_role(user) == "admin" or course.teacher_id == user.id):
        return
    if not user or not user.is_authenticated:
        raise BusinessError(4001, "AUTHENTICATION_REQUIRED", status.HTTP_401_UNAUTHORIZED)
    if get_user_role(user) != "student":
        raise BusinessError(4003, "PERMISSION_DENIED", status.HTTP_403_FORBIDDEN)
    from apps.progress.models import Enrollment

    if not Enrollment.objects.filter(student=user, course=course).exists():
        raise BusinessError(4003, "ENROLLMENT_REQUIRED", status.HTTP_403_FORBIDDEN)


class CourseListCreateView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        queryset = (
            Course.objects.filter(is_deleted=False)
            .select_related("teacher")
            .annotate(chapter_count=Count("chapters"))
            .order_by("-created_at", "-id")
        )
        role = get_user_role(request.user) if request.user and request.user.is_authenticated else None
        queryset = annotate_enrollment_state(queryset, request.user)
        if role == "teacher":
            queryset = queryset.filter(teacher=request.user)
        elif role != "admin":
            queryset = queryset.filter(is_published=True)

        category = request.query_params.get("category")
        level = request.query_params.get("level")
        keyword = request.query_params.get("keyword") or request.query_params.get("search")
        is_published = request.query_params.get("is_published")
        if category:
            queryset = queryset.filter(category=category)
        if level:
            queryset = queryset.filter(level=level)
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)
        if role in {"teacher", "admin"} and is_published in {"true", "false"}:
            queryset = queryset.filter(is_published=is_published == "true")

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CourseSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        assert_teacher_or_admin(request.user)
        serializer = CourseSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        course = serializer.save(teacher=request.user)
        return api_response(CourseSerializer(course, context={"request": request}).data, "course created", status=status.HTTP_201_CREATED)


class CourseDetailView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, course_id):
        course = get_course_for_read(course_id, request.user)
        return api_response(CourseSerializer(course, context={"request": request}).data)

    def put(self, request, course_id):
        course = get_course_for_read(course_id, request.user)
        assert_course_owner(request.user, course)
        serializer = CourseSerializer(course, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        return api_response(CourseSerializer(course, context={"request": request}).data, "course updated")

    def patch(self, request, course_id):
        return self.put(request, course_id)

    def delete(self, request, course_id):
        course = get_course_for_read(course_id, request.user)
        assert_course_owner(request.user, course)
        course.is_deleted = True
        course.is_published = False
        course.save(update_fields=["is_deleted", "is_published", "updated_at"])
        return api_response(None, "course deleted")


class CoursePublishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_course_for_read(course_id, request.user)
        assert_course_owner(request.user, course)
        serializer = CoursePublishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_published = serializer.validated_data["is_published"]
        course.is_published = is_published
        course.published_at = timezone.now() if is_published else None
        course.save(update_fields=["is_published", "published_at", "updated_at"])
        return api_response(CourseSerializer(course, context={"request": request}).data, "course published" if is_published else "course unpublished")


class CourseChapterListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, course_id):
        course = get_course_for_read(course_id, request.user)
        assert_chapter_read_access(request.user, course)
        chapters = course.chapters.prefetch_related("materials").all()
        return api_response(ChapterSerializer(chapters, many=True, context={"request": request}).data)

    def post(self, request, course_id):
        course = get_course_for_read(course_id, request.user)
        assert_course_owner(request.user, course)
        serializer = ChapterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            chapter = serializer.save(course=course)
        except IntegrityError:
            raise BusinessError(4090, "CHAPTER_ORDER_EXISTS", status.HTTP_409_CONFLICT)
        return api_response(ChapterSerializer(chapter, context={"request": request}).data, "chapter created", status=status.HTTP_201_CREATED)


class ChapterDetailView(APIView):
    def put(self, request, chapter_id):
        chapter = get_chapter_for_write(chapter_id, request.user)
        serializer = ChapterSerializer(chapter, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            chapter = serializer.save()
        except IntegrityError:
            raise BusinessError(4090, "CHAPTER_ORDER_EXISTS", status.HTTP_409_CONFLICT)
        return api_response(ChapterSerializer(chapter, context={"request": request}).data, "chapter updated")

    def patch(self, request, chapter_id):
        return self.put(request, chapter_id)

    def delete(self, request, chapter_id):
        chapter = get_chapter_for_write(chapter_id, request.user)
        chapter.delete()
        return api_response(None, "chapter deleted")


class ChapterUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    kind = None

    def post(self, request, chapter_id):
        chapter = get_chapter_for_write(chapter_id, request.user)
        serializer = UploadMaterialSerializer(data=request.data, context={"kind": self.kind})
        serializer.is_valid(raise_exception=True)
        file_obj = serializer.validated_data["file"]
        material, _ = Material.objects.update_or_create(
            chapter=chapter,
            kind=self.kind,
            defaults={
                "file": file_obj,
                "original_name": file_obj.name,
                "content_type": getattr(file_obj, "content_type", "") or "",
                "size": file_obj.size,
            },
        )
        return api_response(MaterialSerializer(material, context={"request": request}).data, "file uploaded")


class ChapterUploadVideoView(ChapterUploadView):
    kind = Material.KIND_VIDEO


class ChapterUploadMaterialView(ChapterUploadView):
    kind = Material.KIND_DOCUMENT


class MaterialDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, material_id):
        material = (
            Material.objects.select_related("chapter", "chapter__course", "chapter__course__teacher")
            .filter(id=material_id, kind=Material.KIND_DOCUMENT, chapter__course__is_deleted=False)
            .first()
        )
        if not material or not material.file:
            raise BusinessError(4040, "MATERIAL_NOT_FOUND", status.HTTP_404_NOT_FOUND)

        course = material.chapter.course
        if not course.is_published and not (
            request.user
            and request.user.is_authenticated
            and (get_user_role(request.user) == "admin" or course.teacher_id == request.user.id)
        ):
            raise BusinessError(4040, "MATERIAL_NOT_FOUND", status.HTTP_404_NOT_FOUND)

        assert_chapter_read_access(request.user, material.chapter.course)

        try:
            response = FileResponse(material.file.open("rb"), content_type=material.content_type or "application/octet-stream")
        except FileNotFoundError:
            raise BusinessError(4040, "MATERIAL_FILE_NOT_FOUND", status.HTTP_404_NOT_FOUND)

        filename = material.original_name or material.file.name.rsplit("/", 1)[-1]
        response["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(filename)}"
        response["Content-Length"] = material.size
        return response
