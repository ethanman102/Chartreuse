import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view
from rest_framework import serializers
from rest_framework.decorators import action, api_view
from ..models import User, Like
from . import users

@extend_schema_view(
    put=extend_schema(
        summary="Adds a like to a post",
        description="Adds a like to a post based on the provided post URL.",
        responses={
            200: OpenApiResponse(description="Like added successfully."),
            404: OpenApiResponse(description="User not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    ),
    delete=extend_schema(
        summary="Removes a like from a post",
        description="Removes a like from a post based on the provided post URL.",
        responses={
            200: OpenApiResponse(description="Like deleted successfully."),
            404: OpenApiResponse(description="User not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
)
@action(detail=True, methods=("PUT", "DELETE"))
@api_view(["PUT", "DELETE"])
@login_required
def like(request, user_id):
    '''
    Adds a like to a post or deletes a like from a post.

    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the user who is liking the post.

    Returns:
        JsonResponse containing the like object.
    '''
    if request.method == 'POST':        
        # Get the post URL from the request body
        postUrl = request.POST.get('post')
        
        # Ensure the user liking the post is the current user
        userLiking = get_object_or_404(User, id=user_id)
        
        # Check if the user has already liked this post
        if Like.objects.filter(user=userLiking, post=postUrl).exists():
            return JsonResponse({"error": "Like already exists."}, status=400)
        
        # Create and save the like
        like = Like(user=userLiking, post=postUrl)
        like.save()

        request.method = 'GET'
        response = users.user(request, user_id)
        data = json.loads(response.content)
        
        # Construct the like object to return in the response
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
        
        return JsonResponse(likeObject, status=200)
    
    if request.method == 'DELETE':
        # Get the post URL from the request body
        postUrl = request.POST.get('post')
        
        # Ensure the user liking the post is the current user
        userLiking = get_object_or_404(User, id=user_id)
        
        # Check if the user has already liked this post
        if not Like.objects.filter(user=userLiking, post=postUrl).exists():
            return JsonResponse({"error": "Like does not exist."}, status=400)
        
        # Create and save the like
        like = Like.objects.filter(user=userLiking, post=postUrl)
        like.delete()

        request.method = 'GET'
        response = users.user(request, user_id)
        data = json.loads(response.content)
        
        # Construct the like object to return in the response
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

        return JsonResponse(likeObject, status=200)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@extend_schema(
    summary="Gets a specific like from a user",
    description=("Gets a specific like object from a user based on the provided like ID and user ID."),
    responses={
        200: OpenApiResponse(description="Successfully retrieved like.",),
        405: OpenApiResponse(description="Method not allowed."),
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
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

@extend_schema(
    summary="Gets all likes on a post",
    description=("Gets all likes on a post based on the provided post ID and user ID."),
    responses={
        200: OpenApiResponse(description="Successfully retrieved all likes.",),
        405: OpenApiResponse(description="Method not allowed."),
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
def likes(request, user_id, post_id):
    '''
    This function handles getting all likes on a post.
    '''
    if request.method == 'GET':
        pass # Placeholder for now since posts have not been implemented yet
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@extend_schema(
    summary="Gets all likes on a comment from a post",
    description=("Gets all likes on a comment from a post based on the provided post ID, comment ID, and user ID."),
    responses={
        200: OpenApiResponse(description="Successfully retrieved all likes."),
        405: OpenApiResponse(description="Method not allowed."),
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
def comment_likes(request, user_id, post_id, comment_id):
    '''
    This function handles getting all likes on a comment.
    '''
    if request.method == 'GET':
        pass # Placeholder for now since posts have not been implemented yet
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@extend_schema(
    summary="Gets all likes made by a user",
    description=("Gets all likes made by a user with the specified user ID."),
    responses={
        200: OpenApiResponse(description="Successfully retrieved all likes."),
        405: OpenApiResponse(description="Method not allowed."),
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
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

@extend_schema(
    summary="Gets a specific like from a user",
    description=("Gets a specific like from a user with the specified user ID."),
    responses={
        200: OpenApiResponse(description="Successfully retrieved the like."),
        405: OpenApiResponse(description="Method not allowed."),
    }
)
@action(detail=True, methods=("GET",))
@api_view(["GET"])
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