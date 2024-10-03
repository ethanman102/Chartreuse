from django.urls import path, include
from .api_handling import likes, users, images, github

app_name = "chartreuse"
urlpatterns = [
    path("api/authors/", users.get_users, name="get_users"),
    path("api/authors/<str:user_id>/", users.user, name="user"),
    path("api/author/", users.create_user, name="create_user"),
    path("api/author/login/", users.login_user, name="login_user"),

    path("api/authors/<str:user_id>/inbox/", likes.like, name="like"),
    path("api/authors/<str:user_id>/posts/<str:post_id>/likes", likes.likes, name="likes"),
    path("api/authors/<str:user_id>/posts/<str:post_id>/comments/<str:comment_id>/likes", likes.comment_likes, name="comment_likes"),

    path("api/authors/<str:user_id>/liked/", likes.liked, name="get_liked"),
    path("api/authors/<str:user_id>/liked/<str:like_id>", likes.like_object, name="get_like_object"),

    path('api/authors/<int:author_id>/posts/<int:post_id>/image', images.get_image_post, name='get_image_post'),

    path("github/<str:user_id>/events/", github.get_events, name="get_events"),
    path("github/<str:user_id>/starred/", github.get_starred, name="get_starred"),
    path("github/<str:user_id>/subscriptions/", github.get_subscriptions, name="get_subscriptions"),

    path('accounts/', include('django.contrib.auth.urls')),
]