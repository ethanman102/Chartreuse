from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import User, FollowRequest, Follow
from django.contrib.auth.decorators import login_required
import json

@login_required
def add_follower(request, author_id, foreign_author_id):
    '''
    Handles follow requests or adding a follower.

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the author to follow.

    Returns:
        JsonResponse with the follow request/follower details.
    '''
    if request.method == 'POST' or request.method == 'PUT':

        author = get_object_or_404(User, id=author_id)
        foreign_author = get_object_or_404(User, id=foreign_author_id)

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
        author_id: The id of the author to unfollow.

    Returns:
        JsonResponse with success message.
    '''
    if request.method == 'DELETE':
        author = get_object_or_404(User, id=author_id)
        foreign_author = get_object_or_404(User, id=foreign_author_id)

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
    # Fetch the author based on the provided author_id
    author = get_object_or_404(User, id=author_id)
    
    # Get all followers for the author
    followers = author.followers.all()

    # Create a list of follower details to be included in the response
    followers_list = [
        {
            "type": "author",
            "id": f"{follower.host}/authors/{follower.id}",
            "host": follower.host,
            "displayName": follower.displayName,
            "page": f"{follower.host}/authors/{follower.id}",
            "github": follower.github,
            "profileImage": follower.profileImage
        }
        for follower in followers
    ]

    # Prepare the final response
    response = {
        "type": "followers",
        "followers": followers_list
    }

    return JsonResponse(response, status=200)

def is_follower(request, author_id, foreign_author_id):
    author = get_object_or_404(User, id=author_id)
    foreign_author = get_object_or_404(User, id=foreign_author_id)

    if Follow.objects.filter(follower=foreign_author, followed=author).exists():
        return JsonResponse({"message": "Is a follower"}, status=200)
    return JsonResponse({"message": "Not a follower"}, status=404)
