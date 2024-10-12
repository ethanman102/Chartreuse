from django.urls import path, re_path
from .api_handling import users, likes, images, github, friends, posts, comments
from .api_handling import followers, follow_requests
from . import views
from .views import ProfileDetailView

app_name = "chartreuse"
urlpatterns = [
    path("api/author/login/", users.UserViewSet.login_user, name="login_user"),

    re_path(r"authors/accept/(?P<followed>.+)/(?P<follower>.+)/", views.follow_accept,name="profile_follow_accept"),
    re_path(r"authors/reject/(?P<followed>.+)/(?P<follower>.+)/", views.follow_reject,name="profile_follow_reject"),
    re_path(r"authors/(?P<url_id>.+)/", ProfileDetailView.as_view(),name="profile"),
    

    # Post URLs
    re_path(r"api/authors/(?P<user_id>.+)/posts/(?P<post_id>.+)", posts.PostViewSet.as_view({"get": "get_post", "delete": "remove_post", "put": "update"}), name="post"),
    re_path(r"api/authors/(?P<user_id>.+)/posts", posts.PostViewSet.as_view({"get": "get_posts", "post": "create_post"}), name="posts"),

    # Comment URLs 
    # path("authors/<str:user_id>/inbox", comments.create_comment, name="create_comment"),
    # path("authors/<str:user_id>/posts/<str:post_id>/comments", comments.get_comments, name="get_comments"),
    # path("authors/<str:user_id>/post/<str:post_id>/comment/<str:remote_comment_id>", comments.get_comment, name="get_comment"),

    # path('authors/<int:author_id>/posts/<int:post_id>/image', images.get_image_post, name='get_image_post'),

    re_path(r"api/authors/(?P<user_id>.+)/inbox/", likes.LikeViewSet.as_view({'post': 'add_like', 'delete': 'remove_like'}), name="like"),
    re_path(r"api/authors/(?P<user_id>.+)/posts/(?P<post_id>.+)/likes", likes.LikeViewSet.get_post_likes, name="post_likes"),
    re_path(r"api/authors/(?P<user_id>.+)/posts/(?P<post_id>.+)/comments/(?P<comment_id>.+)/likes", likes.LikeViewSet.get_comment_likes, name="comment_likes"),

    re_path(r"api/authors/(?P<user_id>.+)/liked/(?P<like_id>.+)", likes.LikeViewSet.get_like, name="get_like_object"),
    re_path(r"api/authors/(?P<user_id>.+)/liked/", likes.LikeViewSet.user_likes, name="get_liked"),

    path('api/authors/<int:author_id>/posts/<int:post_id>/image', images.ImageViewSet.retrieve, name='get_image_post'),

    re_path(r"api/authors/(?P<pk>.+)/$", users.UserViewSet.as_view({'put': 'update', 'delete': 'destroy', 'get': 'retrieve'}), name="user-detail"),
    path("api/authors/", users.UserViewSet.as_view({'post': 'create', 'get': 'list'}), name="user-list"),

    re_path(r"github/(?P<user_id>.+)/events/", github.get_events, name="get_events"),
    re_path(r"github/(?P<user_id>.+)/starred/", github.get_starred, name="get_starred"),
    re_path(r"github/(?P<user_id>.+)/subscriptions/", github.get_subscriptions, name="get_subscriptions"),

    # path('accounts/', include('django.contrib.auth.urls')),
    # For registering a new account
    path("signup", views.signup, name="signup"),
    path("signup/save", views.save_signup, name="save_signup"),
    # For logging in
    path("login", views.login, name="login"),

    # Follower URLs
    re_path(r"api/authors/(?P<author_id>.+)/followers/(?P<foreign_author_id>.+)/is_follower", followers.is_follower, name="is_follower"),
    re_path(r"api/authors/(?P<author_id>.+)/followers/(?P<foreign_author_id>.+)/remove", followers.remove_follower, name="remove_follower"),
    re_path(r"api/authors/(?P<author_id>.+)/followers/(?P<foreign_author_id>.+)", followers.add_follower, name="add_follower"),
    re_path(r"api/authors/(?P<author_id>.+)/followers", followers.get_followers, name="get_followers"),

    # Follow Request URLs
    re_path(r"api/authors/(?P<author_id>.+)/follow-requests/send", follow_requests.send_follow_request, name="send_follow_request"),
    path("api/follow-requests/<int:request_id>/accept", follow_requests.accept_follow_request, name="accept_follow_request"),
    path("api/follow-requests/<int:request_id>/reject", follow_requests.reject_follow_request, name="reject_follow_request"),
    path("api/follow-requests", follow_requests.get_follow_requests, name="get_follow_requests"),

    re_path(r'api/authors/(?P<author_id>.+)/friends/(?P<foreign_author_id>.+)/check_friendship', friends.check_friendship, name='check_friendship'),
    re_path(r"api/authors/(?P<author_id>.+)/friends", friends.get_friends, name="get_friends"),

    
    # for the error page
    path("error", views.error, name="error"),
] 
