from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.responses import api_response
from apps.users.serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    PublicUserSerializer,
    RegisterSerializer,
    SendEmailCodeSerializer,
    UserSerializer,
)
from apps.users.services import register_user, send_register_email_code

User = get_user_model()


class SendEmailCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendEmailCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = send_register_email_code(
            serializer.validated_data["email"],
            request.META.get("REMOTE_ADDR", ""),
        )
        return api_response(data, "验证码已发送")


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_user(**serializer.validated_data)
        return api_response(
            UserSerializer(user, context={"request": request}).data,
            "register success",
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return api_response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user, context={"request": request}).data,
            },
            "login success",
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Stateless JWT logout is handled by the frontend clearing tokens.
        return api_response(None, "logout success")


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        return api_response(UserSerializer(request.user, context={"request": request}).data)

    def put(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return api_response(None, "OLD_PASSWORD_INCORRECT", code=4000, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return api_response(None, "password changed")


class PublicUserProfileView(APIView):
    """Read-only public profile lookup, used for e.g. viewing a community
    post/resource author's info by clicking their avatar."""

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        return api_response(PublicUserSerializer(user, context={"request": request}).data)
