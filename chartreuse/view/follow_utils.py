import json
from urllib.parse import unquote

from chartreuse.models import Follow, FollowRequest, Post, User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_followed(author_id):
    '''
    Retrieves the list of users that the author follows.

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the author whose followed users are being retrieved.

    Returns:
        JsonResponse with the list of followers.
    '''
    decoded_author_id = unquote(author_id)

    # Fetch the author based on the provided author_id
    author = get_object_or_404(User, url_id=decoded_author_id)
    
    # Get all followers for the author
    followed = Follow.objects.filter(follower=author)

    followed_list = []
    
    # Create a list of follower details to be included in the response
    for follower in followed:
        user = follower.followed
        followed_list.append(user)

    return followed_list

def send_follow_request(request):
    """
    Sends a follow request to a user.

    Parameters:
        request: rest_framework object containing the request and query parameters.
    
    Returns:
        JsonResponse containing the follow request status.
    """
    if request.user.is_authenticated:
        body = json.loads(request.body)
        user_id = body["user_id"]
        post_id = body["post_id"]

        print(user_id)
        print(post_id)

        user = User.objects.get(url_id=unquote(user_id))
        post = Post.objects.get(url_id=unquote(post_id))

        post_author = post.user

        # first check if the user has already followed the author
        follow = Follow.objects.filter(follower=user, followed=post_author)

        follow_request= FollowRequest.objects.filter(requester=user, requestee=post_author)
        follow_request_status = None

        if follow:
            follow.delete()
            follow_request_status = "Unfollowed"
        elif follow_request:
            follow_request.delete()
            follow_request_status = "Removed Follow Request"
        else:
            FollowRequest.objects.create(requester=user, requestee=post_author)
            follow_request_status = "Sent Follow Request"

        return JsonResponse({"follow_request_status": follow_request_status})
    else:
        pass