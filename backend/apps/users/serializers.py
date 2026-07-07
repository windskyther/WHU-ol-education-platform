from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from apps.users.models import ensure_user_profile


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    avatar = serializers.ImageField(required=False, allow_null=True, write_only=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "avatar", "avatar_url", "bio", "date_joined")
        read_only_fields = ("id", "email", "role", "avatar_url", "date_joined")

    def get_role(self, obj):
        return ensure_user_profile(obj).role

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = ensure_user_profile(instance)
        data["avatar"] = profile.avatar.name if profile.avatar else None
        data["bio"] = profile.bio
        return data

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        profile = ensure_user_profile(obj)
        if profile.avatar and request:
            return request.build_absolute_uri(profile.avatar.url)
        return None

    def update(self, instance, validated_data):
        avatar = validated_data.pop("avatar", None)
        bio = validated_data.pop("bio", None)
        instance = super().update(instance, validated_data)
        profile = ensure_user_profile(instance)
        changed = False
        if avatar is not None:
            profile.avatar = avatar
            changed = True
        if bio is not None:
            profile.bio = bio
            changed = True
        if changed:
            profile.save()
        return instance


class SendEmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=["register"], default="register", required=False)

    def to_internal_value(self, data):
        if isinstance(data, str):
            data = {"email": data}
        elif isinstance(data, dict):
            data = data.copy()
            for alias in ("registerEmail", "register_email", "mail", "to", "to_email", "emailAddress", "email_address"):
                if "email" not in data and alias in data:
                    data["email"] = data[alias]
            if isinstance(data.get("email"), str):
                data["email"] = data["email"].strip()
        return super().to_internal_value(data)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6, required=False)
    role = serializers.ChoiceField(choices=["student", "teacher"])
    email_code = serializers.CharField(max_length=6, min_length=6)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            if "password_confirm" not in data and "confirmPassword" in data:
                data["password_confirm"] = data["confirmPassword"]
        return super().to_internal_value(data)

    def validate(self, attrs):
        password_confirm = attrs.pop("password_confirm", None)
        if password_confirm is not None and attrs["password"] != password_confirm:
            raise serializers.ValidationError({"password_confirm": "PASSWORD_CONFIRM_MISMATCH"})
        return attrs


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        account = attrs["account"]
        user = User.objects.filter(username=account).first() or User.objects.filter(email=account).first()
        if not user:
            raise serializers.ValidationError("INVALID_CREDENTIALS")
        authenticated = authenticate(username=user.username, password=attrs["password"])
        if not authenticated:
            raise serializers.ValidationError("INVALID_CREDENTIALS")
        attrs["user"] = authenticated
        return attrs
