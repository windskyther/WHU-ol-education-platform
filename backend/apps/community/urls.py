from django.urls import path

from apps.community.views import (
    CategoryListView,
    CommentListCreateView,
    FavoriteToggleView,
    LikeToggleView,
    MyFavoritesView,
    MyPostsView,
    MyResourcesView,
    PostAttachmentUploadView,
    PostDetailView,
    PostListCreateView,
    ResourceDetailView,
    ResourceListCreateView,
)

urlpatterns = [
    path("community/categories/", CategoryListView.as_view(), name="community-category-list"),
    path("community/posts/", PostListCreateView.as_view(), name="community-post-list-create"),
    path("community/posts/<int:post_id>/", PostDetailView.as_view(), name="community-post-detail"),
    path("community/posts/<int:post_id>/attachments/", PostAttachmentUploadView.as_view(), name="community-post-attachment-upload"),
    path("community/resources/", ResourceListCreateView.as_view(), name="community-resource-list-create"),
    path("community/resources/<int:resource_id>/", ResourceDetailView.as_view(), name="community-resource-detail"),
    path(
        "community/<str:target_type>/<int:target_id>/comments/",
        CommentListCreateView.as_view(),
        name="community-comment-list-create",
    ),
    path("community/<str:target_type>/<int:target_id>/like/", LikeToggleView.as_view(), name="community-like-toggle"),
    path("community/<str:target_type>/<int:target_id>/favorite/", FavoriteToggleView.as_view(), name="community-favorite-toggle"),
    path("community/my/posts/", MyPostsView.as_view(), name="community-my-posts"),
    path("community/my/resources/", MyResourcesView.as_view(), name="community-my-resources"),
    path("community/my/favorites/", MyFavoritesView.as_view(), name="community-my-favorites"),
]
