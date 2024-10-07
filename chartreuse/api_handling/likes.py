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
            JsonResponse containing the like object.
        '''
        if request.user.is_authenticated:
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
            user_viewset = UserViewSet() 
            response = user_viewset.retrieve(request, pk=user_id)
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
            return JsonResponse({"error": "User is not authenticated."}, status=401)
    
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
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=user_id)
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
    def get_like(self, request, user_id, like_id):
        '''
        Gets a specific like object from a user.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is liking the posts.
            like_id: The id of the like object.

        Returns:
            JsonResponse containing the like object.
        '''
        user = get_object_or_404(User, id=user_id)

        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=user_id)

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
        page = request.GET.get('page')
        size = request.GET.get('size')

        if (page is None):
            page = 1 # Default page is 1

        if (size is None):
            size = 50 # Default size is 50
        
        user = get_object_or_404(User, id=user_id)
        likes = Like.objects.filter(user=user)

        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=user_id)
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

    @extend_schema(
        summary="Gets a specific like object from a user",
        description="Retrieves a specific like object based on the user ID and like ID.",
        responses={
            200: OpenApiResponse(description="Successfully retrieved the like."),
            404: OpenApiResponse(description="Like or user not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @api_view(["GET"])
    def like_object(request, user_id, like_id):
        '''
        Gets a specific like object from a user.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is liking the posts.
            like_id: The id of the like object.

        Returns:
            JsonResponse containing the like object.
        '''
        user = get_object_or_404(User, id=user_id)

        request.method = 'GET'
        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=user_id)
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