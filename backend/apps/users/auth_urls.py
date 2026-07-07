from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.views import LoginView, LogoutView, RegisterView, SendEmailCodeView


urlpatterns = [
    path("email-code/send/", SendEmailCodeView.as_view(), name="send-email-code"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
