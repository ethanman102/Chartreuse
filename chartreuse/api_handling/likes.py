import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action, api_view

from ..models import Like, User, Post, Comment
from .users import UserSerializer, UserViewSet
from urllib.parse import unquote

class LikeSerializer(serializers.Serializer):
    type = serializers.CharField(default="like")
    author = UserSerializer()
    published = serializers.DateTimeField()
    id = serializers.URLField()
    object = serializers.URLField()

    class Meta:
        fields = ['type', 'author', 'published', 'id', 'object']

class LikesSerializer(serializers.Serializer):
    type = serializers.CharField(default="likes")
    page = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    count = serializers.IntegerField()
    src = LikeSerializer(many=True)

    class Meta:
        fields = ['type', 'page', 'id', 'page_number', 'size', 'count', 'src']

class LikeViewSet(viewsets.ViewSet):
    serializer_class = LikeSerializer

    @extend_schema(
        summary="Adds a like to a post",
        description=(
            "Adds a like to a post based on the provided post URL."
            "\n\n**When to use:** Use this endpoint when a user wants to express appreciation for a post by liking it."
            "\n\n**How to use:** Send a POST request with the user ID in the URL and the post URL in the request body."
            "\n\n**Why to use:** This endpoint provides a way to track and reflect user engagement with posts."
            "\n\n**Why not to use:** Do not use this if the user has already liked the post, or if the user is not authenticated."
        ),
        request=LikeSerializer,
        responses={
            200: OpenApiResponse(description="Like added successfully.", response=LikeSerializer),
            400: OpenApiResponse(
                description="Like already exists.",
                response=inline_serializer(
                    name="LikeAlreadyExistsResponse",
                    fields={"error": serializers.CharField(default="Like already exists.")}
                )
            ),
            400: OpenApiResponse(
                description="Post URL is required.",
                response=inline_serializer(
                    name="PostURLRequiredResponse",
                    fields={"error": serializers.CharField(default="Post URL is required.")}
                )
            ),
            401: OpenApiResponse(
                description="User is not authenticated.",
                response=inline_serializer(
                    name="UserNotAuthenticatedResponse",
                    fields={"error": serializers.CharField(default="User is not authenticated.")}
                )
            ),
            404: OpenApiResponse(
                description="User not found.",
                response=inline_serializer(
                    name="UserNotFoundResponse",
                    fields={"error": serializers.CharField(default="User not found.")}
                )
            ),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed.")}
                )
            ),
        }
    )
    @action(detail=False, methods=["POST"])
    def add_like(self, request, user_id):
        '''
        Adds a like to a post.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is liking the post.

        Returns:
            JsonResponse containing the like object or error messages.
        '''    
        decoded_user_id = unquote(user_id)

        # Get the post URL from the request body
        post_url = request.POST.get('post')
        if not post_url:
            return JsonResponse({"error": "Post URL is required."}, status=400)

        # Ensure the user liking the post is the current user
        user_liking = User.objects.get(pk=decoded_user_id)

        decoded_post_id = unquote(post_url)
        post = Post.objects.get(url_id=decoded_post_id)

        decoded_post_url = unquote(post_url)

        # Check if liking a comment
        comment_url = request.POST.get('comment')
        if comment_url != None:
            decoded_comment_id = unquote(comment_url)
            comment = Comment.objects.get(url_id=decoded_comment_id)
            # Use get_or_create to simplify checking if the user already liked the post
            like, created = Like.objects.get_or_create(user=user_liking, post=post, comment=comment)

        else:
            # Use get_or_create to simplify checking if the user already liked the post
            like, created = Like.objects.get_or_create(user=user_liking, post=post)
        
        if not created:
            return JsonResponse({"error": "Like already exists."}, status=400)
        
        like.save()

        # Reuse the UserViewSet to get author details (using a request object copy if needed)
        user_viewset = UserViewSet()
        user_response = user_viewset.retrieve(request, pk=decoded_user_id)
        
        if user_response.status_code != 200:
            return JsonResponse({"error": "Failed to retrieve user details."}, status=user_response.status_code)
        
        user_data = json.loads(user_response.content)

        # Construct the like object to return in the response
        like_object = {
            "type": "like",
            "author": {
                "type": "author",
                "id": user_data["id"],
                "page": user_data["page"],
                "host": user_data["host"],
                "displayName": user_data["displayName"],
                "github": user_data["github"],
                "profileImage": user_data["profileImage"],
            },
            "published": like.dateCreated,
            "id": like.url_id,
            "object": decoded_post_url
        }
        return JsonResponse(like_object, status=200)
    
    @extend_schema(
        summary="Removes a like from a post",
        description=(
            "Removes a like from a post based on the provided post URL."
            "\n\n**When to use:** Use this endpoint when a user wants to remove their like from a post."
            "\n\n**How to use:** Send a DELETE request with the user ID in the URL and the post URL in the request body."
            "\n\n**Why to use:** This endpoint allows users to retract their engagement on posts by removing the like."
            "\n\n**Why not to use:** Do not use this if the user hasn't liked the post or if the user is not authenticated."
        ),
        request=LikeSerializer,
        responses={
            200: OpenApiResponse(
                description="Like deleted successfully.",
                response=inline_serializer(
                    name="LikeDeletedResponse",
                    fields={"message": serializers.CharField(default="Like deleted successfully.")}
                )
            ),
            400: OpenApiResponse(
                description="Like does not exist.",
                response=inline_serializer(
                    name="LikeDoesNotExistResponse",
                    fields={"error": serializers.CharField(default="Like does not exist.")}
                )
            ),
            404: OpenApiResponse(
                description="User not found.",
                response=inline_serializer(
                    name="UserNotFoundResponse",
                    fields={"error": serializers.CharField(default="User not found.")}
                )
            ),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed.")}
                )
            ),
        }
    )
    @action(detail=False, methods=["DELETE"])
    def remove_like(self, request, user_id):
        '''
        Removes a like from a post.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is liking the post.

        Returns:
            JsonResponse containing the like object.
        '''
        decoded_user_id = unquote(user_id)
        # Get the post URL from the request body
        postUrl = request.POST.get('post')
        decoded_post_url = unquote(postUrl)
        
        # Ensure the user liking the post is the current user
        user_liking = User.objects.get(pk=decoded_user_id)

        post = Post.objects.get(url_id=decoded_post_url)
        
        # Check if the user has already liked this post
        if not Like.objects.filter(user=user_liking, post=post).exists():
            return JsonResponse({"error": "Like does not exist."}, status=400)
        
        # Create and save the like
        like = Like.objects.filter(user=user_liking, post=post)
        like.delete()

        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=decoded_user_id)
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
            "id": like.url_id,
            "object": decoded_post_url
        }

        return JsonResponse(likeObject, status=200)

    @extend_schema(
        summary="Gets a specific like from a user",
        description=(
            "Retrieves a specific like object from a user based on the like ID and user ID."
            "\n\n**When to use:** Use this endpoint when you need to fetch details of a specific like that a user has made on a post."
            "\n\n**How to use:** Send a GET request with the user ID in the URL and the like ID of the desired like object."
            "\n\n**Why to use:** This endpoint provides a way to retrieve details about a specific like, such as when it was made and on which post."
            "\n\n**Why not to use:** Do not use this if the like does not exist or if the user is not authenticated."
        ),
        responses={
            200: OpenApiResponse(description="Successfully retrieved like.", response=LikeSerializer),
            404: OpenApiResponse(
                description="User or like not found.",
                response=inline_serializer(
                    name="UserOrLikeNotFoundResponse",
                    fields={"error": serializers.CharField(default="User or like not found.")}
                )
            ),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed.")}
                )
            ),
        }
    )
    @action(detail=False, methods=["GET"])
    def get_like(request, user_id, like_id):
        '''
        Gets a specific like object from a user.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is liking the posts.
            like_id: The id of the like object.

        Returns:
            JsonResponse containing the like object.
        '''
        decoded_user_id = unquote(user_id)
        decoded_like_id = unquote(like_id)

        print(decoded_user_id)
        print(decoded_like_id)
    
        user = User.objects.get(pk=decoded_user_id)

        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=decoded_user_id)

        data = json.loads(response.content)
        like = Like.objects.filter(user=user, url_id=decoded_like_id).first()

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
            "id": like.url_id,
            "object": like.post.url_id
        }
        return JsonResponse(likeObject, safe=False)

    @extend_schema(
        summary="Gets all likes on a post",
        description=(
            "Gets all likes on a post based on the provided post ID and user ID."
            "\n\n**When to use:** Use this endpoint to fetch a list of likes on a post."
            "\n\n**How to use:** Send a GET request with the `user_id` and `post_id` in the URL."
            "\n\n**Why to use:** This API helps in getting all likes related to a post, useful for tracking engagement."
            "\n\n**Why not to use:** If the post doesn't exist, or if you do not require all likes on a post."
        ),
        responses={
            200: OpenApiResponse(description="Successfully retrieved all likes.", response=LikesSerializer),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed.")}
                )
            ),
        }
    )
    @action(detail=False, methods=["GET"])
    def get_post_likes(self, request, user_id=None, post_id=None):
        '''
        This function handles getting all likes on a post.
        '''
        decoded_user_id = unquote(user_id)
        decoded_post_id = unquote(post_id)

        user = get_object_or_404(User, url_id=decoded_user_id)
        post = get_object_or_404(Post, url_id=decoded_post_id)

        likes = Like.objects.filter(user=user, post=post)

        request.method = 'GET'
        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=decoded_user_id)

        data = json.loads(response.content)

        page = request.GET.get('page')
        size = request.GET.get('size')

        if (page is None):
            page = 1 # Default page is 1

        if (size is None):
            size = 50 # Default size is 50
        
        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=decoded_user_id)
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
                "id": like.url_id,
                "object": like.post.url_id
            }

            filtered_likes_attributes.append(likeObject)

        userLikes = {
            "type": "likes",
            "page": str(user.url_id) + "/posts/",
            "page_number": page,
            "size": size,
            "count": len(likes),
            "src": filtered_likes_attributes
        }

        return JsonResponse(userLikes, safe=False)

    @extend_schema(
        summary="Gets all likes on a comment from a post",
        description=(
            "Gets all likes on a comment from a post based on the provided post ID, comment ID, and user ID."
            "\n\n**When to use:** Use this endpoint when you need to fetch all the likes for a particular comment."
            "\n\n**How to use:** Send a GET request with the `user_id`, `post_id`, and `comment_id` in the URL."
            "\n\n**Why to use:** This endpoint is helpful to track how many likes a specific comment has received."
            "\n\n**Why not to use:** If you're not interested in the comment likes or if the comment doesn't exist."
        ),
        responses={
            200: OpenApiResponse(description="Successfully retrieved all likes.", response=LikesSerializer),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed.")}
                )
            ),
        }
    )
    @action(detail=False, methods=["GET"])
    def get_comment_likes(self, request, user_id, post_id, comment_id):
        '''
        This function handles getting all likes on a comment.
        '''
        decoded_user_id = unquote(user_id)
        decoded_post_id = unquote(post_id)
        decoded_comment_id = unquote(comment_id)
    
        user = get_object_or_404(User, url_id=decoded_user_id)
        post = get_object_or_404(Post, url_id=decoded_post_id)
        comment = get_object_or_404(Comment, url_id=decoded_comment_id)

        likes = Like.objects.filter(user=user, post=post, comment=comment)

        request.method = 'GET'
        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=decoded_user_id)

        data = json.loads(response.content)

        page = request.GET.get('page', 1)   # Default page is 1
        size = request.GET.get('size', 50)  # Default size is 50
        
        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=decoded_user_id)
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
                "id": like.url_id,
                "object": like.post.url_id
            }

            filtered_likes_attributes.append(likeObject)

        userLikes = {
            "type": "likes",
            "page": str(post.url_id),
            "id": str(comment.url_id) + "/likes/",
            "page_number": page,
            "size": size,
            "count": len(likes),
            "src": filtered_likes_attributes
        }

        return JsonResponse(userLikes, safe=False)

    @extend_schema(
        summary="Gets all likes made by a user",
        description=(
            "Retrieves all likes made by a user based on the user ID, with optional pagination."
            "\n\n**When to use:** Use this endpoint to list all the posts or comments a user has liked."
            "\n\n**How to use:** Send a GET request with the `user_id` in the URL. Optionally, include `page` and `size` query parameters for pagination."
            "\n\n**Why to use:** To track all the posts and comments that a particular user has liked."
            "\n\n**Why not to use:** If you are not interested in a user's likes or if the user ID is not valid."
        ),
        request=UserSerializer,
        parameters=[
            OpenApiParameter(name="page", description="Page number for pagination.", required=False, type=int),
            OpenApiParameter(name="size", description="Number of likes per page.", required=False, type=int),
        ],
        responses={
            200: OpenApiResponse(description="Successfully retrieved all likes.", response=LikesSerializer),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed.")}
                )
            ),
        }
    )
    @api_view(["GET"])
    def user_likes(request, user_id):
        '''
        Gets all the likes of a user.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is liking the posts.

        Returns:
            JsonResponse containing the like objects.
        '''
        decoded_user_id = unquote(user_id)
        page = request.GET.get('page')
        size = request.GET.get('size')

        if (page is None):
            page = 1 # Default page is 1

        if (size is None):
            size = 50 # Default size is 50
        
        user = get_object_or_404(User, url_id=decoded_user_id)
        likes = Like.objects.filter(user=user)

        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=decoded_user_id)
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
                "id": like.url_id,
                "object": like.post.url_id
            }

            filtered_likes_attributes.append(likeObject)

        userLikes = {
            "type": "likes",
            "page": str(user.url_id) + "/posts/",
            "page_number": page,
            "size": size,
            "count": len(likes),
            "src": filtered_likes_attributes
        }

        return JsonResponse(userLikes, safe=False)