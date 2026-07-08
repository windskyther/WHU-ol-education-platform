from django.urls import path

from apps.courses.views import (
    ChapterDetailView,
    ChapterUploadMaterialView,
    ChapterUploadVideoView,
    CourseChapterListCreateView,
    CourseDetailView,
    CourseListCreateView,
    CoursePublishView,
    MaterialDownloadView,
)


urlpatterns = [
    path("courses/", CourseListCreateView.as_view(), name="course-list-create"),
    path("courses/<int:course_id>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<int:course_id>/publish/", CoursePublishView.as_view(), name="course-publish"),
    path("courses/<int:course_id>/chapters/", CourseChapterListCreateView.as_view(), name="course-chapters"),
    path("chapters/<int:chapter_id>/", ChapterDetailView.as_view(), name="chapter-detail"),
    path("chapters/<int:chapter_id>/upload-video/", ChapterUploadVideoView.as_view(), name="chapter-upload-video"),
    path("chapters/<int:chapter_id>/upload-material/", ChapterUploadMaterialView.as_view(), name="chapter-upload-material"),
    path("materials/<int:material_id>/download/", MaterialDownloadView.as_view(), name="material-download"),
]
