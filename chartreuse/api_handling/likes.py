import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated

from ..models import Like, User
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
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    @extend_schema(
        summary="Adds a like to a post",
        description="Adds a like to a post based on the provided post URL.",
        responses={
            200: OpenApiResponse(description="Like added successfully.", response=LikeSerializer),
            400: OpenApiResponse(description="Like already exists."),
            401: OpenApiResponse(description="User is not authenticated."),
            404: OpenApiResponse(description="User not found."),
            405: OpenApiResponse(description="Method not allowed."),
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
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
    
        decoded_user_id = unquote(user_id)

        # Get the post URL from the request body
        post_url = request.POST.get('post')
        if not post_url:
            return JsonResponse({"error": "Post URL is required."}, status=400)

        # Ensure the user liking the post is the current user
        user_liking = User.objects.get(pk=decoded_user_id)

        decoded_post_url = unquote(post_url)    
        
        # Use get_or_create to simplify checking if the user already liked the post
        like, created = Like.objects.get_or_create(user=user_liking, post=decoded_post_url)
        
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
        description="Removes a like from a post based on the provided post URL.",
        responses={
            200: OpenApiResponse(description="Like deleted successfully.", response=LikeSerializer),
            400: OpenApiResponse(description="Like does not exist."),
            404: OpenApiResponse(description="User not found."),
            405: OpenApiResponse(description="Method not allowed."),
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
        
        # Check if the user has already liked this post
        if not Like.objects.filter(user=user_liking, post=decoded_post_url).exists():
            return JsonResponse({"error": "Like does not exist."}, status=400)
        
        # Create and save the like
        like = Like.objects.filter(user=user_liking, post=decoded_post_url)
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
        description="Retrieves a specific like object from a user based on the like ID and user ID.",
        responses={
            200: OpenApiResponse(description="Successfully retrieved like.", response=LikeSerializer),
            404: OpenApiResponse(description="User or like not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @api_view(["GET"])
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
    
        user = User.objects.get(pk=decoded_user_id)

        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=decoded_user_id)

        data = json.loads(response.content)
        like = Like.objects.filter(user=user, url_id=decoded_like_id)[0]

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
            "object": like.post
        }
        return JsonResponse(likeObject, safe=False)

    @extend_schema(
        summary="Gets all likes on a post",
        description=("Gets all likes on a post based on the provided post ID and user ID."),
        responses={
            200: OpenApiResponse(description="Successfully retrieved all likes.", response=LikesSerializer),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @api_view(["GET"])
    def get_post_likes(self, request, user_id, post_id):
        '''
        This function handles getting all likes on a post.
        '''
        pass # Placeholder for now since posts have not been implemented yet

    @extend_schema(
        summary="Gets all likes on a comment from a post",
        description=("Gets all likes on a comment from a post based on the provided post ID, comment ID, and user ID."),
        responses={
            200: OpenApiResponse(description="Successfully retrieved all likes."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @api_view(["GET"])
    def get_comment_likes(self, request, user_id, post_id, comment_id):
        '''
        This function handles getting all likes on a comment.
        '''
        pass # Placeholder for now since posts have not been implemented yet

    @extend_schema(
        summary="Gets all likes made by a user",
        description="Retrieves all likes made by a user based on the user ID, with optional pagination.",
        parameters=[
            OpenApiParameter(name="page", description="Page number for pagination.", required=False, type=int),
            OpenApiParameter(name="size", description="Number of likes per page.", required=False, type=int),
        ],
        responses={
            200: OpenApiResponse(description="Successfully retrieved all likes."),
            405: OpenApiResponse(description="Method not allowed."),
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
                "object": like.post
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