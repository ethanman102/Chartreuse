from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import Follow, User

def get_friends(request, author_id):
    author = get_object_or_404(User, id=author_id)

    # Get the followers of the author
    followers = Follow.objects.filter(followed=author)

    # Get the authors that the current author follows
    following = Follow.objects.filter(follower=author)

    friends = set(f.followed for f in followers).intersection(set(f.follower for f in following))

    friend_list = [
        {
            "type": "author",
            "id": f"{friend.host}/authors/{friend.id}",
            "host": friend.host,
            "displayName": friend.displayName,
            "page": f"{friend.host}/authors/{friend.id}",
            "github": friend.github,
            "profileImage": friend.profileImage
        }
        for friend in friends
    ]

    response = {
        "type": "friends",
        "friends": friend_list
    }

    return JsonResponse(response, status=200)

def check_friendship(request, author_id):
    author = get_object_or_404(User, id=author_id)

    # Check if the current user follows the author and vice versa
    is_friend = (
        Follow.objects.filter(follower=request.user, followed=author).exists() and
        Follow.objects.filter(follower=author, followed=request.user).exists()
    )

    return JsonResponse({'is_friend': is_friend})