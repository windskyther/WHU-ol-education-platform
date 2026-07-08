from django.urls import path

from apps.progress.views import CourseEnrollView, CourseProgressView, MyCoursesView, ProgressUpdateView


urlpatterns = [
    path("courses/<int:course_id>/enroll/", CourseEnrollView.as_view(), name="course-enroll"),
    path("my/courses/", MyCoursesView.as_view(), name="my-courses"),
    path("progress/update/", ProgressUpdateView.as_view(), name="progress-update"),
    path("progress/course/<int:course_id>/", CourseProgressView.as_view(), name="course-progress"),
]
