from django.urls import path

from apps.qa.views import (
    CourseQuestionAnswerView,
    CourseQuestionDetailView,
    CourseQuestionListCreateView,
    CourseQuestionResolveView,
)


urlpatterns = [
    path("courses/<int:course_id>/questions/", CourseQuestionListCreateView.as_view(), name="course-question-list-create"),
    path("course-questions/<int:question_id>/", CourseQuestionDetailView.as_view(), name="course-question-detail"),
    path("course-questions/<int:question_id>/answer/", CourseQuestionAnswerView.as_view(), name="course-question-answer"),
    path("course-questions/<int:question_id>/resolve/", CourseQuestionResolveView.as_view(), name="course-question-resolve"),
]
