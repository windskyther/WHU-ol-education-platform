from django.urls import path

from apps.users.views import ChangePasswordView, MeView, PublicUserProfileView


urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("me/password/", ChangePasswordView.as_view(), name="change-password"),
    path("<int:user_id>/", PublicUserProfileView.as_view(), name="user-public-profile"),
]
