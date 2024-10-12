from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import User, FollowRequest, Follow
from django.contrib.auth.decorators import login_required
import json
from urllib.parse import unquote
from rest_framework.permissions import IsAuthenticated

@login_required
def add_follower(request, author_id, foreign_author_id):
    '''
    Handles follow requests or adding a follower.

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the current author.
        foreign_author_id: The id of the author who is becoming a follower

    Returns:
        JsonResponse with the follower details.
    '''
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated."}, status=401)

    if request.method == 'POST' or request.method == 'PUT':

        decoded_user_id = unquote(user_id)
        decoded_foreign_author_id = unquote(foreign_author_id)

        author = get_object_or_404(User, id=decoded_author_id)
        foreign_author = get_object_or_404(User, id=decoded_foreign_author_id)

        # Check if the user already follows the author
        if Follow.objects.filter(follower=foreign_author, followed=author).exists():
            return JsonResponse({"message": "Already a follower"}, status=400)

        # Create and save a follower object
        Follow.objects.create(follower=foreign_author, followed=author)
        return JsonResponse({"message": "Follower added"}, status=201)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


@login_required
def remove_follower(request, author_id, foreign_author_id):
    '''
    Handles unfollowing an author.

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the current author
        foreign_author_id: The id of the author to unfollow

    Returns:
        JsonResponse with success message.
    '''
    if request.method == 'DELETE':
        decoded_author_id = unquote(author_id)
        decoded_foreign_author_id = unquote(foreign_author_id)

        author = get_object_or_404(User, id=decoded_author_id)
        foreign_author = get_object_or_404(User, id=decoded_foreign_author_id)

        # Check if the user is following the author
        follow = Follow.objects.filter(follower=foreign_author, followed=author)

        if not follow.exists():
            return JsonResponse({"error": "Not a follower."}, status=400)

        # Remove the follower
        follow.delete()

        return JsonResponse({"message": "Follower removed."}, status=204)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


def get_followers(request, author_id):
    '''
    Retrieves the list of followers for a specific author.

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the author whose followers are being retrieved.

    Returns:
        JsonResponse with the list of followers.
    '''
    decoded_author_id = unquote(author_id)

    # Fetch the author based on the provided author_id
    author = get_object_or_404(User, id=decoded_author_id)
    
    # Get all followers for the author
    followers = Follow.objects.filter(followed=author)

    followers_list = []

    # Create a list of follower details to be included in the response
    for follower in followers:
        user = follower.follower
        follower_attributes = [
            {
                "type": "author",
                "id": f"{user.host}/authors/{user.user.id}",
                "host": user.host,
                "displayName": user.displayName,
                "page": f"{user.host}/authors/{user.user.id}",
                "github": user.github,
                "profileImage": user.profileImage
            }
        ]
        followers_list.append(follower_attributes)

    # Prepare the final response
    response = {
        "type": "followers",
        "followers": followers_list
    }

    return JsonResponse(response, status=200)

def is_follower(request, author_id, foreign_author_id):
    '''
    Checks if a particular author is a follower of current author

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the current author
        foreign_author_id: The id of the author to unfollow

    Returns:
        JsonResponse with success message.
    '''
    decoded_author_id = unquote(author_id)
    decoded_foreign_author_id = unquote(foreign_author_id)

    author = get_object_or_404(User, id=decoded_author_id)
    foreign_author = get_object_or_404(User, id=decoded_foreign_author_id)

    if Follow.objects.filter(follower=foreign_author, followed=author).exists():
        return JsonResponse({"message": "Is a follower"}, status=200)
    return JsonResponse({"message": "Not a follower"}, status=404)
