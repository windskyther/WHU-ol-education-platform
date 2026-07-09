from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.exceptions import BusinessError
from apps.common.pagination import StandardPagination
from apps.common.permissions import get_user_role
from apps.common.responses import api_response
from apps.community.models import (
    POST_CATEGORY_CHOICES,
    RESOURCE_CATEGORY_CHOICES,
    TARGET_POST,
    TARGET_RESOURCE,
    Comment,
    Favorite,
    Like,
    Post,
    PostAttachment,
    Resource,
)
from apps.community.serializers import (
    CommentSerializer,
    PostAttachmentSerializer,
    PostAttachmentUploadSerializer,
    PostSerializer,
    ResourceSerializer,
)

TARGET_MODELS = {
    TARGET_POST: Post,
    TARGET_RESOURCE: Resource,
}


def get_target_model(target_type):
    model = TARGET_MODELS.get(target_type)
    if not model:
        raise BusinessError(4040, "TARGET_TYPE_NOT_SUPPORTED", status.HTTP_404_NOT_FOUND)
    return model


def get_target_instance(target_type, target_id):
    model = get_target_model(target_type)
    instance = model.objects.filter(id=target_id, is_deleted=False).first()
    if not instance:
        raise BusinessError(4040, "TARGET_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    return instance


def get_post_for_write(post_id, user):
    post = Post.objects.filter(id=post_id, is_deleted=False).first()
    if not post:
        raise BusinessError(4040, "POST_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    if post.author_id != user.id and get_user_role(user) != "admin":
        raise BusinessError(4003, "POST_OWNER_REQUIRED", status.HTTP_403_FORBIDDEN)
    return post


def get_resource_for_write(resource_id, user):
    resource = Resource.objects.filter(id=resource_id, is_deleted=False).first()
    if not resource:
        raise BusinessError(4040, "RESOURCE_NOT_FOUND", status.HTTP_404_NOT_FOUND)
    if resource.author_id != user.id and get_user_role(user) != "admin":
        raise BusinessError(4003, "RESOURCE_OWNER_REQUIRED", status.HTTP_403_FORBIDDEN)
    return resource


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Post.objects.filter(is_deleted=False).select_related("author").prefetch_related("attachments")
        keyword = request.query_params.get("keyword")
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = PostSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def post(self, request):
        serializer = PostSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=request.user)
        return api_response(PostSerializer(post, context={"request": request}).data, "post created", status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = Post.objects.filter(id=post_id, is_deleted=False).select_related("author").prefetch_related("attachments").first()
        if not post:
            raise BusinessError(4040, "POST_NOT_FOUND", status.HTTP_404_NOT_FOUND)
        return api_response(PostSerializer(post, context={"request": request}).data)

    def patch(self, request, post_id):
        post = get_post_for_write(post_id, request.user)
        serializer = PostSerializer(post, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(serializer.data, "post updated")

    def delete(self, request, post_id):
        post = get_post_for_write(post_id, request.user)
        post.is_deleted = True
        post.save(update_fields=["is_deleted", "updated_at"])
        return api_response(None, "post deleted")


class PostAttachmentUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, post_id):
        post = get_post_for_write(post_id, request.user)
        files = request.FILES.getlist("file")
        if not files:
            raise BusinessError(4000, "ATTACHMENT_FILE_REQUIRED", status.HTTP_400_BAD_REQUEST)
        attachments = []
        for file_obj in files:
            serializer = PostAttachmentUploadSerializer(data={"file": file_obj})
            serializer.is_valid(raise_exception=True)
            attachments.append(
                PostAttachment.objects.create(
                    post=post,
                    file=file_obj,
                    original_name=file_obj.name,
                    content_type=getattr(file_obj, "content_type", "") or "",
                    size=file_obj.size,
                )
            )
        return api_response(
            PostAttachmentSerializer(attachments, many=True, context={"request": request}).data,
            "attachment uploaded",
            status=status.HTTP_201_CREATED,
        )


class ResourceListCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Resource.objects.filter(is_deleted=False).select_related("author")
        keyword = request.query_params.get("keyword")
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
        has_url = request.query_params.get("has_url")
        if has_url == "true":
            queryset = queryset.exclude(url="")
        elif has_url == "false":
            queryset = queryset.filter(url="")
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ResourceSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def post(self, request):
        serializer = ResourceSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        resource = serializer.save(author=request.user)
        return api_response(
            ResourceSerializer(resource, context={"request": request}).data,
            "resource created",
            status=status.HTTP_201_CREATED,
        )


class ResourceDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated]

    def get(self, request, resource_id):
        resource = Resource.objects.filter(id=resource_id, is_deleted=False).select_related("author").first()
        if not resource:
            raise BusinessError(4040, "RESOURCE_NOT_FOUND", status.HTTP_404_NOT_FOUND)
        return api_response(ResourceSerializer(resource, context={"request": request}).data)

    def patch(self, request, resource_id):
        resource = get_resource_for_write(resource_id, request.user)
        serializer = ResourceSerializer(resource, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(serializer.data, "resource updated")

    def delete(self, request, resource_id):
        resource = get_resource_for_write(resource_id, request.user)
        resource.is_deleted = True
        resource.save(update_fields=["is_deleted", "updated_at"])
        return api_response(None, "resource deleted")


class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, target_type, target_id):
        get_target_instance(target_type, target_id)
        queryset = Comment.objects.filter(target_type=target_type, target_id=target_id).select_related("author")
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CommentSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def post(self, request, target_type, target_id):
        instance = get_target_instance(target_type, target_id)
        serializer = CommentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(author=request.user, target_type=target_type, target_id=target_id)
        model = get_target_model(target_type)
        model.objects.filter(id=instance.id).update(comments_count=instance.comments_count + 1)
        return api_response(
            CommentSerializer(comment, context={"request": request}).data,
            "comment created",
            status=status.HTTP_201_CREATED,
        )


class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, target_type, target_id):
        instance = get_target_instance(target_type, target_id)
        model = get_target_model(target_type)
        existing = Like.objects.filter(user=request.user, target_type=target_type, target_id=target_id).first()
        if existing:
            existing.delete()
            model.objects.filter(id=instance.id).update(likes_count=max(instance.likes_count - 1, 0))
            liked = False
        else:
            Like.objects.create(user=request.user, target_type=target_type, target_id=target_id)
            model.objects.filter(id=instance.id).update(likes_count=instance.likes_count + 1)
            liked = True
        instance.refresh_from_db()
        return api_response({"liked": liked, "likes_count": instance.likes_count}, "like toggled")


class FavoriteToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, target_type, target_id):
        instance = get_target_instance(target_type, target_id)
        model = get_target_model(target_type)
        existing = Favorite.objects.filter(user=request.user, target_type=target_type, target_id=target_id).first()
        if existing:
            existing.delete()
            model.objects.filter(id=instance.id).update(favorites_count=max(instance.favorites_count - 1, 0))
            favorited = False
        else:
            Favorite.objects.create(user=request.user, target_type=target_type, target_id=target_id)
            model.objects.filter(id=instance.id).update(favorites_count=instance.favorites_count + 1)
            favorited = True
        instance.refresh_from_db()
        return api_response({"favorited": favorited, "favorites_count": instance.favorites_count}, "favorite toggled")


class MyPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = (
            Post.objects.filter(author=request.user, is_deleted=False)
            .select_related("author")
            .prefetch_related("attachments")
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = PostSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class MyResourcesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Resource.objects.filter(author=request.user, is_deleted=False).select_related("author")
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ResourceSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class MyFavoritesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target_type = request.query_params.get("type")
        if target_type not in (TARGET_POST, TARGET_RESOURCE):
            raise BusinessError(4000, "FAVORITE_TYPE_REQUIRED", status.HTTP_400_BAD_REQUEST)
        favorite_ids = list(
            Favorite.objects.filter(user=request.user, target_type=target_type).order_by("-created_at").values_list("target_id", flat=True)
        )
        paginator = StandardPagination()
        page_ids = paginator.paginate_queryset(favorite_ids, request)
        model = get_target_model(target_type)
        serializer_class = PostSerializer if target_type == TARGET_POST else ResourceSerializer
        items_by_id = {}
        qs = model.objects.filter(id__in=page_ids, is_deleted=False).select_related("author")
        if target_type == TARGET_POST:
            qs = qs.prefetch_related("attachments")
        for item in qs:
            items_by_id[item.id] = item
        ordered_items = [items_by_id[item_id] for item_id in page_ids if item_id in items_by_id]
        serializer = serializer_class(ordered_items, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)


class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target_type = request.query_params.get("target")
        if target_type == TARGET_POST:
            choices = POST_CATEGORY_CHOICES
        elif target_type == TARGET_RESOURCE:
            choices = RESOURCE_CATEGORY_CHOICES
        else:
            raise BusinessError(4000, "CATEGORY_TARGET_REQUIRED", status.HTTP_400_BAD_REQUEST)
        data = [{"value": value, "label": label} for value, label in choices]
        return api_response(data)
