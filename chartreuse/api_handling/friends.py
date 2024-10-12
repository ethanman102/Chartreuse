from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import Follow, User
from urllib.parse import unquote

def get_friends(request, author_id):
    '''
    Retrieves the list of friends for a specific author.

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the author whose friends are being retrieved.

    Returns:
        JsonResponse with the list of friends.
    '''
    decoded_author_id = unquote(author_id)
    author = get_object_or_404(User, url_id=decoded_author_id)

    # Get the followers of the author
    followers = Follow.objects.filter(followed=author).values_list('follower', flat=True)

    # Get the authors that the current author follows
    following = Follow.objects.filter(follower=author).values_list('followed', flat=True)

    friends = User.objects.filter(url_id__in=followers).filter(url_id__in=following)

    friends_list = []

    for friend in friends:
        friend_attributes = {
            "type": "author",
            "id": f"{friend.host}/authors/{friend.url_id}",
            "host": friend.host,
            "displayName": friend.displayName,
            "page": f"{friend.host}/authors/{friend.url_id}",
            "github": friend.github,
            "profileImage": friend.profileImage
        }
        friends_list.append(friend_attributes)


    response = {
        "type": "friends",
        "friends": friends_list
    }

    return JsonResponse(response, status=200)

def check_friendship(request, author_id, foreign_author_id):
    '''
    Checks if two authors are friends (mutual followers).

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the current author
        foreign_author_id: The id of the author to check friendship with

    Returns:
        JsonResponse with a message indicating friendship status.
    '''
    decoded_author_id = unquote(author_id)
    decoded_foreign_author_id = unquote(foreign_author_id)

    author = get_object_or_404(User, url_id=decoded_author_id)
    foreign_author = get_object_or_404(User, url_id=decoded_foreign_author_id)

    # Check if the current user follows the author and vice versa
    if (Follow.objects.filter(follower=author, followed=foreign_author).exists() and
        Follow.objects.filter(follower=foreign_author, followed=author).exists()):
        return JsonResponse({"message": "Authors are friends"}, status=200)

    return JsonResponse({"message": "Authors are not friends"}, status=404)