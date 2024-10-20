from django.urls import path, re_path
from .api_handling import users, likes, images, github, friends, posts
from .api_handling import followers, follow_requests
from django.conf import settings
from django.conf.urls.static import static
from chartreuse.views import  error, test
from .view import home_page_view, signup_view, login_view, landing_page_view, profile_view, follow_list_view, support_functions, post_view

app_name = "chartreuse"
urlpatterns = [
    # Like URLs
    re_path(r"api/authors/(?P<user_id>.+\d)/inbox/$", likes.LikeViewSet.as_view({'post': 'add_like', 'delete': 'remove_like'}), name="like"),
    re_path(r"api/authors/(?P<user_id>.+\d)/posts/(?P<post_id>.+\d)/likes/$", likes.LikeViewSet.get_post_likes, name="post_likes"),
    re_path(r"api/authors/(?P<user_id>.+\d)/posts/(?P<post_id>.+\d)/comments/(?P<comment_id>.+\d)/likes/$", likes.LikeViewSet.get_comment_likes, name="comment_likes"),

    re_path(r"api/authors/(?P<user_id>.+\d)/liked/(?P<like_id>.+\d)/$", likes.LikeViewSet.get_like, name="get_like_object"),
    re_path(r"api/authors/(?P<user_id>.+\d)/liked/$", likes.LikeViewSet.user_likes, name="get_liked"),

    # Post URLs
    re_path(r"api/authors/(?P<user_id>.+\d)/posts/(?P<post_id>.+\d)/$", posts.PostViewSet.as_view({"get": "get_post", "delete": "remove_post", "put": "update"}), name="post"),
    re_path(r"api/authors/(?P<user_id>.+\d)/posts/$", posts.PostViewSet.as_view({"get": "get_posts", "post": "create_post"}), name="posts"),

    # Author URLs
    path("api/author/login/", users.UserViewSet.login_user, name="login_user"),
    re_path(r"api/authors/(?P<pk>.+\d)/$", users.UserViewSet.as_view({'put': 'update', 'delete': 'destroy', 'get': 'retrieve'}), name="user-detail"),
    path("api/authors/", users.UserViewSet.as_view({'post': 'create', 'get': 'list'}), name="user-list"),

    # Follower API URLs
    re_path(r"api/authors/(?P<author_id>.+\d)/followers/(?P<foreign_author_id>.+\d)/is_follower", followers.FollowViewSet.as_view({'get': 'is_follower'}), name="is_follower"),
    re_path(r"api/authors/(?P<author_id>.+\d)/followers/(?P<foreign_author_id>.+\d)/remove", followers.FollowViewSet.as_view({'delete': 'remove_follower'}), name="remove_follower"),
    re_path(r"api/authors/(?P<author_id>.+\d)/followers/(?P<foreign_author_id>.+\d)", followers.FollowViewSet.as_view({'post': 'add_follower', 'put': 'add_follower'}), name="add_follower"),
    re_path(r"api/authors/(?P<author_id>.+\d)/followers", followers.FollowViewSet.as_view({'get': 'get_followers'}), name="get_followers"),

    # Follow Request API URLs
    re_path(r"api/authors/(?P<author_id>.+\d)/follow-requests/send", follow_requests.FollowRequestViewSet.as_view({'post': 'send_follow_request'}), name="send_follow_request"),
    path("api/follow-requests/<int:request_id>/accept", follow_requests.FollowRequestViewSet.as_view({'post': 'accept_follow_request'}), name="accept_follow_request"),
    path("api/follow-requests/<int:request_id>/reject", follow_requests.FollowRequestViewSet.as_view({'delete': 'reject_follow_request'}), name="reject_follow_request"),
    path("api/follow-requests", follow_requests.FollowRequestViewSet.as_view({'get': 'get_follow_requests'}), name="get_follow_requests"),

    # Friend API URLs
    re_path(r'api/authors/(?P<author_id>.+\d)/friends/(?P<foreign_author_id>.+\d)/check_friendship', friends.FriendsViewSet.as_view({'get': 'check_friendship'}), name='check_friendship'),
    re_path(r"api/authors/(?P<author_id>.+\d)/friends", friends.FriendsViewSet.as_view({'get': 'get_friends'}), name="get_friends"),

    # Image URLs
    path('api/authors/<int:author_id>/posts/<int:post_id>/image', images.ImageViewSet.retrieve, name='get_image_post'),

    # Github URLs
    re_path(r"github/(?P<user_id>.+)/events/", github.get_events, name="get_events"),
    re_path(r"github/(?P<user_id>.+)/starred/", github.get_starred, name="get_starred"),
    re_path(r"github/(?P<user_id>.+)/subscriptions/", github.get_subscriptions, name="get_subscriptions"),
    
    # error page url
    path("error/", error, name="error"),

    # UI testing page -- for debugging
    path("test/", test, name="test"),

    # UI Related URLs
    path('', landing_page_view.landing_page, name='home'),
    path('signup/', signup_view.signup, name='signup'),
    path('signup/save/', signup_view.save_signup, name='save_signup'),

    path('login/', login_view.login, name='login'),
    path('logout/', login_view.logout, name='logout'),
    path('login/authenticate/', login_view.save_login, name='authenticate'),

    path("homepage/", home_page_view.FeedDetailView.as_view(), name="homepage"),
    path('add-post/', support_functions.add_post, name='add_post'),
    path('add-post/save/', support_functions.save_post, name='save_post'),

    re_path(r'.+/like-post/', support_functions.like_post, name='like-post'),
    re_path(r'.+/send-follow-request/', support_functions.send_follow_request, name='send-follow-request'),

    re_path(r'homepage/post/(?P<post_id>.+)/edit/', support_functions.edit_post, name='edit-post'),
    re_path(r'homepage/post/(?P<post_id>.+)/delete/', support_functions.delete_post, name='delete-post'),
    re_path(r'homepage/post/(?P<post_id>.+)/update/', support_functions.update_post, name='update-post'),
    re_path(r'homepage/post/(?P<post_id>.+)/', post_view.PostDetailView.as_view(), name='view-post'),

    # Follow Request URLs
    re_path(r"authors/(?P<url_id>.+)/post/(?P<post_id>.+)/",post_view.PostDetailView.as_view(),name="profile_view_post"),
    re_path(r"authors/accept/(?P<followed>.+)/(?P<follower>.+)/", profile_view.follow_accept,name="profile_follow_accept"),
    re_path(r"authors/reject/(?P<followed>.+)/(?P<follower>.+)/", profile_view.follow_reject,name="profile_follow_reject"),
    re_path(r"authors/unfollow/(?P<followed>.+)/(?P<follower>.+)/",profile_view.profile_unfollow,name="profile_unfollow"),
    re_path(r"authors/followrequest/(?P<requestee>.+)/(?P<requester>.+)/",profile_view.profile_follow_request,name="profile_follow_request"),
    re_path(r"authors/following/(?P<user_id>.+)/",follow_list_view.FollowListDetailView.as_view(),name="user_following_list"),
    re_path(r"authors/followers/(?P<user_id>.+)/",follow_list_view.FollowListDetailView.as_view(),name="user_followers_list"),
    re_path(r"authors/friends/(?P<user_id>.+)/",follow_list_view.FollowListDetailView.as_view(),name="user_friends_list"),
    re_path(r"authors/(?P<url_id>.+)/", profile_view.ProfileDetailView.as_view(),name="profile"),
    re_path(r"authors/", support_functions.view_profile ,name="redirect_profile"),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
