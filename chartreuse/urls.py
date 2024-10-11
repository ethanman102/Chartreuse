from django.urls import path
from .api_handling import users, likes, images, github, friends
from .api_handling import followers, follow_requests
from . import views
from .views import ProfileDetailView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/authors', users.UserViewSet, basename='user')

app_name = "chartreuse"
urlpatterns = [
    path("api/author/login/", users.UserViewSet.login_user, name="login_user"),

    path("authors/<int:pk>/", ProfileDetailView.as_view(),name="profile"),

    path("api/authors/<str:user_id>/inbox/", likes.LikeViewSet.as_view({'post': 'add_like', 'delete': 'remove_like'}), name="like"),
    path("api/authors/<str:user_id>/posts/<str:post_id>/likes", likes.LikeViewSet.get_post_likes, name="post_likes"),
    path("api/authors/<str:user_id>/posts/<str:post_id>/comments/<str:comment_id>/likes", likes.LikeViewSet.get_comment_likes, name="comment_likes"),

    path("api/authors/<str:user_id>/liked/", likes.LikeViewSet.user_likes, name="get_liked"),
    path("api/authors/<str:user_id>/liked/<str:like_id>", likes.LikeViewSet.like_object, name="get_like_object"),

    path('api/authors/<int:author_id>/posts/<int:post_id>/image', images.ImageViewSet.retrieve, name='get_image_post'),

    path("github/<str:user_id>/events/", github.get_events, name="get_events"),
    path("github/<str:user_id>/starred/", github.get_starred, name="get_starred"),
    path("github/<str:user_id>/subscriptions/", github.get_subscriptions, name="get_subscriptions"),

    # path('accounts/', include('django.contrib.auth.urls')),
    # For registering a new account
    path("signup", views.signup, name="signup"),
    path("signup/save", views.save_signup, name="save_signup"),
    # For logging in
    path("login", views.login, name="login"),

    # Follower URLs
    path("api/authors/<str:author_id>/followers/<str:foreign_author_id>/", followers.add_follower, name="add_follower"),
    path("api/authors/<str:author_id>/followers/<str:foreign_author_id>/remove/", followers.remove_follower, name="remove_follower"),
    path("api/authors/<str:author_id>/followers/", followers.get_followers, name="get_followers"),
    path("api/authors/<str:author_id>/followers/<str:foreign_author_id>/is_follower/", followers.is_follower, name="is_follower"),

    # Follow Request URLs
    path("api/authors/<str:author_id>/inbox/", follow_requests.send_follow_request, name="send_follow_request"),
    path("api/follow-requests/<int:request_id>/accept/", follow_requests.accept_follow_request, name="accept_follow_request"),
    path("api/follow-requests/<int:request_id>/reject/", follow_requests.reject_follow_request, name="reject_follow_request"),
    path("api/follow-requests/", follow_requests.get_follow_requests, name="get_follow_requests"),

    path("api/authors/<str:author_id>/friends/", friends.get_friends, name="get_friends"),
    path('api/authors/<str:author_id>/friends/<str:foreign_author_id>/check_friendship/', friends.check_friendship, name='check_friendship'),

] + router.urls