from django.urls import path, re_path
from .api_handling import users, likes, images, github, friends, posts, comments
from .api_handling import followers, follow_requests
from django.conf import settings
from django.conf.urls.static import static
from chartreuse.views import  error, test
from django.contrib.auth.decorators import login_required
from .view import home_page_view, profile_utils, signup_view, login_view, landing_page_view, profile_view, follow_list_view, post_view, settings_view, post_utils, comment_utils, follow_utils,discover_view, inbox
app_name = "chartreuse"
urlpatterns = [
    re_path(r"homepage/post/(?P<post_id>https?.+\w)/image$", images.retrieve_from_homepage, name='get_image_post'),
    re_path(r"authors/(?P<author_id>.+)/post/(?P<post_id>https?.+\w)/image$", images.retrieve_from_profile, name='get_image_post_profile'),

    # Post Comment URLs
    re_path(r"comment/$",comment_utils.add_comment,name="add_comment"),
    re_path(r"comment/(?P<comment_id>.+)/delete/$",comment_utils.delete_comment,name="delete_comment"),
    re_path(r"comment/like/$",comment_utils.like_comment,name="like_comment"),

    # Inbox URL
    re_path(r"api/authors/(?P<user_id>.+\w)/inbox/$", inbox.inbox, name="inbox"),

    # Like URLs
    re_path(r"api/authors/(?P<user_id>.+\w)/like/$", likes.LikeViewSet.as_view({'post': 'add_like', 'delete': 'remove_like'}), name="like"),
    re_path(r"api/authors/(?P<user_id>.+\w)/posts/(?P<post_id>.+\w)/comments/(?P<comment_id>.+\w)/likes/$", likes.LikeViewSet.as_view({'get': 'get_comment_likes'}), name="comment_likes"),
    # re_path(r"api/authors/(?P<user_id>.+\w)/posts/(?P<post_id>.+\w)/likes/$", likes.LikeViewSet.get_post_likes, name="post_likes"),
    re_path(r"api/authors/(?P<user_id>.+\w)/posts/(?P<post_id>.+\w)/likes/$", likes.LikeViewSet.as_view({'get': 'get_post_likes'}), name="post_likes"),
    re_path(r"api/authors/(?P<user_id>https?.+\w)/liked/(?P<like_id>https?.+\w)/$", likes.LikeViewSet.get_like, name="get_like_object"),
    re_path(r"api/authors/(?P<user_id>.+\w)/liked/$", likes.LikeViewSet.user_likes, name="get_liked"),

    # Comment URLs 
    re_path(r"api/authors/(?P<user_id>https?.+\w)/posts/(?P<post_id>https?.+\w)/comments/add/$", comments.CommentViewSet.as_view({'post': 'create_comment'}), name="create_comment"),
    re_path(r"api/authors/(?P<user_id>https?.+\w)/posts/(?P<post_id>https?.+\w)/comment/(?P<comment_id>.+)/$", comments.CommentViewSet.get_comment, name="get_comment"),
    re_path(r"api/comment/(?P<comment_id>.+)/remove/$", comments.CommentViewSet.as_view({"delete":"delete_comment"}), name="delete_comment"), 
    re_path(r"api/comment/(?P<comment_id>.+)/$", comments.CommentViewSet.get_comment, name="get_comment_by_cid"), 
    re_path(r"api/authors/(?P<user_id>https?.+\w)/posts/(?P<post_id>https?.+\w)/comments/$", comments.CommentViewSet.as_view({'get': 'get_comments'}), name="get_comments"),
    re_path(r"api/posts/(?P<post_id>https?.+\w)/comments/$", comments.CommentViewSet.as_view({'get': 'get_comments'}), name="get_comments_by_pid"),
    re_path(r"api/authors/(?P<user_id>https?.+\w)/commented/$", comments.CommentViewSet.as_view({'get': "get_authors_comments", 'post': "create_comment"}), name="get_authors_comments"),
    re_path(r"api/authors/(?P<user_id>https?.+\w)/commented/(?P<comment_id>.+)/$", comments.CommentViewSet.get_comment, name="get_commented"),
    re_path(r"api/commented/(?P<comment_id>.+)/$", comments.CommentViewSet.get_comment, name="get_commented_by_cid"), 

    # Post URLs
    re_path(r"api/authors/(?P<user_id>https?.+\w)/posts/(?P<post_id>https?.+\w)/$", posts.PostViewSet.as_view({"get": "get_post", "delete": "remove_post", "put": "update"}), name="post"),
    re_path(r"api/authors/(?P<user_id>.+\w)/posts/$", posts.PostViewSet.as_view({"get": "get_posts", "post": "create_post"}), name="posts"),
    re_path(r"api/post-exists/$", post_utils.check_duplicate_post, name="check_duplicate_post"),

    # Follower API URLs
    re_path(r"api/authors/(?P<author_id>.+\w)/followers/(?P<foreign_author_id>.+\w)/is_follower", followers.FollowViewSet.as_view({'get': 'is_follower'}), name="is_follower"),
    re_path(r"api/authors/(?P<author_id>.+\w)/followers/(?P<foreign_author_id>.+\w)/remove", followers.FollowViewSet.as_view({'delete': 'remove_follower'}), name="remove_follower"),
    re_path(r"api/authors/(?P<author_id>.+\w)/followers/(?P<foreign_author_id>.+\w)", followers.FollowViewSet.as_view({'post': 'add_follower', 'put': 'add_follower'}), name="add_follower"),
    re_path(r"api/authors/(?P<author_id>.+\w)/followers", followers.FollowViewSet.as_view({'get': 'get_followers'}), name="get_followers"),
    
    # Author URLs
    path("api/author/login/", users.UserViewSet.login_user, name="login_user"),
    re_path(r"api/authors/(?P<pk>.+\w)/$", users.UserViewSet.as_view({'put': 'update', 'delete': 'destroy', 'get': 'retrieve'}), name="user-detail"),
    path("api/authors/", users.UserViewSet.as_view({'post': 'create', 'get': 'list'}), name="user-list"),

    
    # Follow Request API URLs
    re_path(r"api/authors/(?P<author_id>.+\w)/follow-requests/send", follow_requests.FollowRequestViewSet.as_view({'post': 'send_follow_request'}), name="send_follow_request"),
    path("api/follow-requests/<int:request_id>/accept", follow_requests.FollowRequestViewSet.as_view({'post': 'accept_follow_request'}), name="accept_follow_request"),
    path("api/follow-requests/<int:request_id>/reject", follow_requests.FollowRequestViewSet.as_view({'delete': 'reject_follow_request'}), name="reject_follow_request"),
    path("api/follow-requests", follow_requests.FollowRequestViewSet.as_view({'get': 'get_follow_requests'}), name="get_follow_requests"),

    # Friend API URLs
    re_path(r'api/authors/(?P<author_id>.+\w)/friends/(?P<foreign_author_id>.+\w)/check_friendship', friends.FriendsViewSet.as_view({'get': 'check_friendship'}), name='check_friendship'),
    re_path(r"api/authors/(?P<author_id>.+\w)/friends", friends.FriendsViewSet.as_view({'get': 'get_friends'}), name="get_friends"),

    # Image URLs
 
    path('set-profile-image/', profile_utils.setNewProfileImage, name='set_profile_image'),

    # Github URLs
    re_path(r"github/(?P<user_id>https?.+\w)/events/", github.get_events, name="get_events"),
    re_path(r"github/(?P<user_id>https?.+\w)/starred/", github.get_starred, name="get_starred"),
    re_path(r"github/(?P<user_id>https?.+\w)/subscriptions/", github.get_subscriptions, name="get_subscriptions"),
    re_path(r"github/polling/$", profile_utils.checkGithubPolling, name="github_polling"),
    
    # error page url
    path("error/", error, name="error"),

    # UI testing page -- for debugging
    path("test/", test, name="test"),

    #settings URLS:
    path('settings/updatePassword/',settings_view.update_password,name='update_password'),
    path('settings/removeGithub/',settings_view.remove_github,name="remove_github"),
    path('settings/addGithub/',settings_view.add_github,name="add_github"),
    path('settings/updateDisplayName/',settings_view.update_display_name,name="update_display_name"),
    path('settings/uploadProfileImage/',settings_view.upload_profile_picture,name='upload_profile_picture'),
    path('settings/uploadImageUrl/',settings_view.upload_url_picture,name='upload_url_picture'),
    path('settings/',login_required(settings_view.SettingsDetailView.as_view(),login_url='chartreuse:login'),name="settings"),

    # discover views urls:
    re_path(r'discover/(?P<host>.+)/',login_required(discover_view.DiscoverAuthorListView.as_view(),login_url='chartreuse:login'),name='discover_authors'),
    path('discover/',login_required(discover_view.DiscoverNodeListView.as_view(),login_url='chartreuse:login'),name="discover_nodes"),


    # UI Related URLs
    path('', landing_page_view.landing_page, name='home'),
    path('signup/', signup_view.signup, name='signup'),
    path('signup/save/', signup_view.save_signup, name='save_signup'),

    path('login/', login_view.login, name='login'),
    path('logout/', login_view.logout, name='logout'),
    path('login/authenticate/', login_view.save_login, name='authenticate'),

    path("homepage/", home_page_view.FeedDetailView.as_view(), name="homepage"),
    path('add-post/', post_utils.add_post, name='add_post'),
    path('add-post/save/', post_utils.save_post, name='save_post'),

    re_path(r'.+/like-post/', post_utils.like_post, name='like-post'),
    re_path(r'.+/send-follow-request/', follow_utils.send_follow_request, name='send-follow-request'),
    re_path(r'.+/repost/', post_utils.repost,name='repost'),

    re_path(r'homepage/post/(?P<post_id>https?.+\w)/edit/', post_utils.edit_post, name='edit-post'),
    re_path(r'homepage/post/(?P<post_id>https?.+\w)/delete/', post_utils.delete_post, name='delete-post'),
    re_path(r'homepage/post/(?P<post_id>https?.+\w)/update/', post_utils.update_post, name='update-post'),
    re_path(r'homepage/post/(?P<post_id>https?.+\w)/', post_view.PostDetailView.as_view(), name='view-post'),

    # Follow Request URLs
    re_path(r"authors/(?P<url_id>.+)/post/(?P<post_id>https?.+\w)/$",post_view.PostDetailView.as_view(),name="profile_view_post"),
    re_path(r"authors/accept/(?P<followed>.+)/(?P<follower>.+)/", profile_view.follow_accept,name="profile_follow_accept"),
    re_path(r"authors/reject/(?P<followed>.+)/(?P<follower>.+)/", profile_view.follow_reject,name="profile_follow_reject"),
    re_path(r"authors/unfollow/(?P<followed>.+)/(?P<follower>.+)/",profile_view.profile_unfollow,name="profile_unfollow"),
    re_path(r"authors/followrequest/(?P<requestee>.+)/(?P<requester>.+)/",profile_view.profile_follow_request,name="profile_follow_request"),
    re_path(r"authors/following/(?P<user_id>https?.+\w)/",follow_list_view.FollowListDetailView.as_view(),name="user_following_list"),
    re_path(r"authors/followers/(?P<user_id>https?.+\w)/",follow_list_view.FollowListDetailView.as_view(),name="user_followers_list"),
    re_path(r"authors/friends/(?P<user_id>https?.+\w)/",follow_list_view.FollowListDetailView.as_view(),name="user_friends_list"),
    re_path(r"authors/(?P<url_id>.+)/", profile_view.ProfileDetailView.as_view(),name="profile"),
    re_path(r"authors/", profile_utils.view_profile ,name="redirect_profile"),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
