from django.urls import path

from apps.exams.views import (
    CourseExamListCreateView,
    ExamDetailView,
    ExamQuestionCreateView,
    ExamSubmissionListView,
    ExamSubmitView,
    MyScoresView,
    QuestionDetailView,
)


urlpatterns = [
    path("courses/<int:course_id>/exams/", CourseExamListCreateView.as_view(), name="course-exams"),
    path("exams/<int:exam_id>/", ExamDetailView.as_view(), name="exam-detail"),
    path("exams/<int:exam_id>/questions/", ExamQuestionCreateView.as_view(), name="exam-question-create"),
    path("questions/<int:question_id>/", QuestionDetailView.as_view(), name="question-detail"),
    path("exams/<int:exam_id>/submit/", ExamSubmitView.as_view(), name="exam-submit"),
    path("my/scores/", MyScoresView.as_view(), name="my-scores"),
    path("exams/<int:exam_id>/submissions/", ExamSubmissionListView.as_view(), name="exam-submissions"),
]
