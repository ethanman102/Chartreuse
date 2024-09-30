from django.urls import path, include
from .api_handling import likes, users

app_name = "chartreuse"
urlpatterns = [
    path("api/authors/", users.get_users, name="get_users"),
    path("api/authors/<str:user_id>/", users.user, name="user"),
    path("api/author/", users.create_user, name="create_user"),
    path("api/author/login/", users.login_user, name="login_user"),

    path("authors/<str:user_id>/inbox/", likes.like, name="like"),
    path("authors/<str:user_id>/posts/<str:post_id>/likes", likes.likes, name="likes"),
    path("authors/<str:user_id>/posts/<str:post_id>/comments/<str:comment_id>/likes", likes.comment_likes, name="comment_likes"),

    path("authors/<str:user_id>/liked/", likes.liked, name="get_liked"),
    path("authors/<str:user_id>/liked/<str:like_id>", likes.like_object, name="get_like_object"),

    path('accounts/', include('django.contrib.auth.urls')),
]