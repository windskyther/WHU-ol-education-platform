from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.responses import api_response
from apps.users.serializers import LoginSerializer, RegisterSerializer, SendEmailCodeSerializer, UserSerializer
from apps.users.services import register_user, send_register_email_code


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
