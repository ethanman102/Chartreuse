from django.urls import path
from . import users

app_name = "chartreuse"
urlpatterns = [
    path("api/users/", users.get_users, name="get_users"),
    path("api/users/<str:user_id>/", users.user, name="user"),
    path("api/user/", users.create_user, name="create_user"),
    path("api/user/<str:user_id>/password/", users.change_password, name="change_password"),
]