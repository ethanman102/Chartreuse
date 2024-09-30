from django.http import JsonResponse
from django.core.paginator import Paginator
from ..models import User, Like
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from . import users
import json

@login_required
def like(request, user_id):
    '''
    Adds a like to a post.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the user who is liking the post.

    Returns:
        JsonResponse containing the like object.
    '''
    if request.method == 'POST':
        currentUser = request.user

        postUrl = request.POST.get('post')
        userLiking = get_object_or_404(User, user=currentUser)

        request.user = userLiking.user
        request.method = 'GET'
        response = users.user(request, user_id)

        data = json.loads(response.content)

        like = Like.objects.create(user=userLiking, post=postUrl)

        likeObject = {
            "type": "like",
            "author": {
                "type": "author",
                "id": data["id"],
                "page": data["page"],
                "host": data["host"],
                "displayName": data["displayName"],
                "github": data["github"],
                "profileImage": data["profileImage"]
            },
            "published": like.dateCreated,
            "id": userLiking.host + "authors/" + str(userLiking.id) + "/liked/" + str(like.id),
            "object": postUrl
        }

        return JsonResponse(likeObject, status = 200)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def likes(request, user_id, post_id):
    '''
    This function handles getting all likes on a post.
    '''
    if request.method == 'GET':
        pass # Placeholder for now since posts have not been implemented yet
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def comment_likes(request, user_id, post_id, comment_id):
    '''
    This function handles getting all likes on a comment.
    '''
    if request.method == 'GET':
        pass # Placeholder for now since posts have not been implemented yet
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def liked(request, user_id):
    '''
    Gets all the likes of a user.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the user who is liking the posts.

    Returns:
        JsonResponse containing the like objects.
    '''
    if request.method == 'GET':
        page = request.GET.get('page')
        size = request.GET.get('size')

        if (page is None):
            page = 1 # Default page is 1

        if (size is None):
            size = 50 # Default size is 50
        
        user = get_object_or_404(User, id=user_id)
        likes = Like.objects.filter(user=user)

        request.method = 'GET'
        response = users.user(request, user_id)

        data = json.loads(response.content)
        
        # Paginates likes based on the size
        likes_paginator = Paginator(likes, size)

        page_likes = likes_paginator.page(page)

        # Since we have some additional fields, we only want to return the required ones
        filtered_likes_attributes = []
        for like in page_likes:

            likeObject = {
                "type": "likes",
                "author": {
                    "type": "author",
                    "id": data["id"],
                    "page": data["page"],
                    "host": data["host"],
                    "displayName": data["displayName"],
                    "github": data["github"],
                    "profileImage": data["profileImage"]
                },
                "published": like.dateCreated,
                "id": user.host + "authors/" + str(user.id) + "/liked/" + str(like.id),
                "object": like.post
            }

            filtered_likes_attributes.append(likeObject)

        userLikes = {
            "type": "likes",
            "page": user.host + "authors/" + str(user.id) + "/posts/",
            "page_number": page,
            "size": size,
            "count": len(likes),
            "src": filtered_likes_attributes
        }

        return JsonResponse(userLikes, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def like_object(request, user_id, like_id):
    '''
    Gets a specific like object from a user.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the user who is liking the posts.
        like_id: The id of the like object.

    Returns:
        JsonResponse containing the like object.
    '''
    if request.method == 'GET':
        user = get_object_or_404(User, id=user_id)

        request.method = 'GET'
        response = users.user(request, user_id)

        data = json.loads(response.content)
        like = Like.objects.filter(user=user, id=like_id)[0]

        likeObject = {
            "type": "like",
            "author": {
                "type": "author",
                "id": data["id"],
                "page": data["page"],
                "host": data["host"],
                "displayName": data["displayName"],
                "github": data["github"],
                "profileImage": data["profileImage"]
            },
            "published": like.dateCreated,
            "id": user.host + "authors/" + str(user.id) + "/liked/" + str(like.id),
            "object": like.post
        }
        return JsonResponse(likeObject, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)