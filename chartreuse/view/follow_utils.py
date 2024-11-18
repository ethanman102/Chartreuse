import json
from urllib.parse import unquote,quote

from chartreuse.models import Follow, FollowRequest, Post, User, Node
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import requests

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
            if post_author.host != user.host:
                # case of following remotely!!

                # check to see if we are following such a node...
                node_queryset = Node.objects.filter(host=post_author.host,status='ENABLED',follow_status='OUTGOING')
                if not node_queryset.exists():
                    return JsonResponse({"follow_request_status": 'Node is disabled, follow rejected'})

                node = node_queryset[0]
                auth = (node.username,node.password)

                headers = {
                    "Content-Type": "application/json; charset=utf-8"
                }

                data = {
                'type': 'follow',
                'summary':'actor wants to follow object',
                'actor':
                    {
                        'type':'author',
                        'id': user.url_id,
                        'host': user.host,
                        'displayName': user.displayName,
                        'page': f'{user.host}/authors/{user.url_id}/',
                        'github':user.github,
                        'profileImage': user.profileImage
                    },
                    'object':{
                        'type':'author',
                        'id': post_author.url_id,
                        'host': post_author.host,
                        'displayName': post_author.displayName,
                        'page': f'{post_author.host}/authors/{post_author.url_id}/',
                        'github':post_author.github,
                        'profileImage': post_author.profileImage
                    }
                }

                url = f"{post_author.host}authors/{quote(post_author.url_id,safe='')}/inbox/"
                try:
                    requests.post(url, headers=headers, json=data, auth=auth)
                    follow_request_status = "Sent Follow Request"
                    new_follow = Follow.objects.create(followed=post_author,follower=user)
                except: 
                    return JsonResponse({"follow_request_status": 'Error Following...'})
                
            else:
                FollowRequest.objects.create(requester=user, requestee=post_author)
                follow_request_status = "Sent Follow Request"

        return JsonResponse({"follow_request_status": follow_request_status})
    else:
        pass