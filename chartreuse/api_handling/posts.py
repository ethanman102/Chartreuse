import json

from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated

from ..models import User, Like, Post, Follow, Comment
from .users import UserSerializer, UserViewSet
from .likes import LikeSerializer, LikesSerializer, LikeViewSet
from .comments import CommentSerializer, CommentsSerializer, CommentViewSet
from .friends import check_friendship

class PostSerializer(serializers.Serializer):
    type = serializers.CharField(default="post")
    title = serializers.CharField()
    id = serializers.URLField()
    decription = serializers.CharField()
    contentType = serializers.CharField()
    content = serializers.CharField()
    author = UserSerializer()
    comments = CommentsSerializer()
    likes = LikesSerializer()
    published = serializers.DateTimeField()
    visibility = serializers.CharField(default="PUBLIC")

    class Meta:
        fields = ['type', 'title', 'id', 'decription', 'contentType', 'content', 'author', 'comments', 'likes', 'published', 'visibility']

class PostViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    @extend_schema(
        summary="Adds a post",
        description="Adds a post based on the on author URL",
        parameters=[
            OpenApiParameter(name="visibility", description="visibilility of the post.", required=False, type=str),
            OpenApiParameter(name="title", description="title of the post.", requred=True, type=str),
            OpenApiParameter(name="description", description="the description of the post.", required=False, type=str),
            OpenApiParameter(name="contentType", description="the contentType of teh post.", required=False, type=str),
            OpenApiParameter(name="content", description="content of the post.", required=True, type=str),
        ],
        responses = {
            201: OpenApiResponse(description="Post created successfully.", response=PostSerializer),
            400: OpenApiResponse(description="Request syntax invalid."),
            401: OpenApiResponse(description="User is not authenticated."),
            404: OpenApiResponse(description="User is not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @action(detail=False, methods=["POST"])
    def create_post(self, request, user_id):
        """
        Creates a new post.
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is creating the post.
            
        Returns:
            JsonResponce containing the new post    
        """

        if request.user.is_authenticated:
            # Ensure the user creating the post is the current user
            author = get_object_or_404(User, id=user_id)

            # Create and save the post
            post = Post(user=author)
            post.save()

            post_type = request.POST.get("visibility")
            post_title = request.POST.get("title")
            # TODO: generate the post id
            post_id = None
            post_description = request.POST.get("description")
            contentType_description = request.POST.get("contentType")
            content_description = request.POST.get("content")
            # TODO: generate current date
            post_published = request.POST.get("published")

            request.method = "GET"
            user_viewset = UserViewSet()
            response = user_viewset.retrieve(request, pk=user_id)
            author_data = json.loads(response.content)

            # Construct the post object to return in the responce
            if post_type in ["PUBLIC", "FRIENDS", "UNLISTED", "DELETED"]:
                postObject = {
                    "type": "post",
                    "title": post_title,
                    "id": post_id,
                    "description": post_description,
                    "contentType": contentType_description,
                    "content": content_description,
                    "author": {
                        "type": "author",
                        "id": author_data["id"],
                        "page": author_data["page"],
                        "host": author_data["host"],
                        "displayName": author_data["displayName"],
                        "github": author_data["github"],
                        "profileImage": author_data["profileImage"]
                    },
                    "published": post_published,
                    "visibility": post_type,
                }

            else:
                return JsonResponse({"error": "post visibliity invalid"}, status=400)

            return JsonResponse(postObject, status=201)

        else:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
        

    @extend_schema(
        summary="Removes a post",
        description="Removes a post based on the provided post URL.",
        parameters=[
            OpenApiParameter(name="post", description="the post url.", required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(description="Post deleted successfully.", response=PostSerializer),
            400: OpenApiResponse(description="Post does not exist."),
            404: OpenApiResponse(description="User not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @action(detail=False, methods=["DELETE"])
    def remove_post(self, request, user_id, post_id):
        """
        Reassigns the status of a post to DELETED.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is liking the post.

        Returns:
            JsonResponse containing the like object.
        """
        if request.user.is_authenticated:
            # Get the post URL from the request body
            post_url = request.POST.get("post")

            # Ensure the user deleting the post is the current user
            author = get_object_or_404(User, pk=user_id)

            # Check if the post was previously created
            if not Post.objects.filter(user=author, pk=post_url).exists():
                return JsonResponse({"error": "Post does not exists."})

            # Delete the post
            post = Post.objects.filter(user=author, post=post_url)
            post.update(visibility="DELETED")

            # get the post data
            request.method = "GET"
            user_viewset = UserViewSet()
            response = user_viewset.retrieve(request, pk=user_id)
            data = json.loads(response.content)

            user_viewset = UserViewSet()
            response = user_viewset.retrieve(request, pk=user_id)
            author_data = json.loads(response.content)

            comments_viewset = CommentViewSet()
            response = comments_viewset.retrieve(request, pk=post_url)
            comments_data = json.loads(response.content)

            likes_viewset = LikeViewSet()
            response = likes_viewset.retrieve(request, pk=post_url)
            likes_data = json.loads(response.content)

            # Construct the post object to return in the responce
            postObject = {
                "type": "post",
                "title": post.title,
                "id": post_url,
                "description": post.description,
                "contentType": post.contentType,
                "content": post.content,
                "author": {
                    "type": "author",
                    "id": author_data["id"],
                    "page": author_data["page"],
                    "host": author_data["host"],
                    "displayName": author_data["displayName"],
                    "github": author_data["github"],
                    "profileImage": author_data["profileImage"]
                },
                "comments":{
                    "type": "comments",
                    "page": comments_data["page"],
                    "id": comments_data["id"],
                    "page_number": comments_data["page_number"],
                    "size": comments_data["size"],
                    "count": comments_data["count"],
                    "src": comments_data["src"]
                },
                "likes": {
                    "types": "likes",
                    "page": likes_data["page"],
                    "id": likes_data["id"],
                    "page_number": likes_data["page_number"],
                    "size": likes_data["size"],
                    "count": likes_data["count"],
                    "src": likes_data["src"]
                },
                "published": post.published,
                "visibility": post.visiblity,
            }

            return JsonResponse(postObject, status=200)

        else:
            return JsonResponse({"error": "Method not allowed."}, status=405) 
        

    @extend_schema(
            summary="Gets a specific post from a user",
            description="Retrieves a specific post object from a user based on the user id and post id",
            parameters=[
            OpenApiParameter(name="user_id", description="The id of the user requesting the post.", required=False, type=str),
        ],
            responses={
                200: OpenApiResponse(description="Successfully retrieved post.", response=PostSerializer),
                400: OpenApiResponse(description="This is a FRIENDS only post and user and author are not friends"),
                401: OpenApiResponse(description="The user is not authenticated."),
                404: OpenApiResponse(description="User or post not found."),
                405: OpenApiResponse(description="Method not allowed."),
            }
    )
    @api_view(["GET"])
    def get_post(self, request, user_id, post_id):
        """
        Gets a specific post object from a user.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who created the posts.
            post_id: The id of the post object.

        Returns:
            JsonResponse containing the post object.
        """
        author = get_object_or_404(User, id=user_id)
        request_user_id = request.GET.get("user_id")
        is_authenticated = request.user.is_authenticated
        post = Post.objects.filter(user=author, id=post_id)[0]

        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=user_id)
        author_data = json.loads(response.content)
    
        comments_viewset = CommentViewSet()
        response = comments_viewset.retrieve(request, pk=post_id)
        comments_data = json.loads(response.content)

        likes_viewset = LikeViewSet()
        response = likes_viewset.retrieve(request, pk=post_id)
        likes_data = json.loads(response.content)
    
        if post.visibility in ["PUBLIC", "UNLISTED"]:
            postObject = {
                "type": "post",
                "title": post.title,
                "id": post.id,
                "description": post.description,
                "contentType": post.contentType,
                "content": post.content,
                "author": {
                    "type": "author",
                    "id": author_data["id"],
                    "page": author_data["page"],
                    "host": author_data["host"],
                    "displayName": author_data["displayName"],
                    "github": author_data["github"],
                    "profileImage": author_data["profileImage"]
                },
                "comments":{
                    "type": "comments",
                    "page": comments_data["page"],
                    "id": comments_data["id"],
                    "page_number": comments_data["page_number"],
                    "size": comments_data["size"],
                    "count": comments_data["count"],
                    "src": comments_data["src"]
                },
                "likes": {
                    "types": "likes",
                    "page": likes_data["page"],
                    "id": likes_data["id"],
                    "page_number": likes_data["page_number"],
                    "size": likes_data["size"],
                    "count": likes_data["count"],
                    "src": likes_data["src"]
                },
                "published": post.published,
                "visibility": post.visibility,
            }

        elif post.visibility == "FRIENDS":
            # check if the current user is the authors friend
            if is_authenticated:
                response = check_friendship(request, user_id, request_user_id)

                if response.status_code() == 200:
                    postObject = {
                        "type": "post",
                        "title": post.title,
                        "id": post.id,
                        "description": post.description,
                        "contentType": post.contentType,
                        "content": post.content,
                        "author": {
                            "type": "author",
                            "id": author_data["id"],
                            "page": author_data["page"],
                            "host": author_data["host"],
                            "displayName": author_data["displayName"],
                            "github": author_data["github"],
                            "profileImage": author_data["profileImage"]
                        },
                        "comments":{
                            "type": "comments",
                            "page": comments_data["page"],
                            "id": comments_data["id"],
                            "page_number": comments_data["page_number"],
                            "size": comments_data["size"],
                            "count": comments_data["count"],
                            "src": comments_data["src"]
                        },
                        "likes": {
                            "types": "likes",
                            "page": likes_data["page"],
                            "id": likes_data["id"],
                            "page_number": likes_data["page_number"],
                            "size": likes_data["size"],
                            "count": likes_data["count"],
                            "src": likes_data["src"]
                        },
                        "published": post.published,
                        "visibility": post.visibility,
                    } 

                else:
                    JsonResponse({"error": "This user must be a friend of the author to view this post"}, status=400)       
            else:
                JsonResponse({"error": "The user is not authenticated."}, status=401)
        else:
            return JsonResponse({"error": "Post does not exist."}, status=404)
        
        return JsonResponse(postObject, status=200)

    @extend_schema(
        summary="Updates the post",
        description="Updates the post using the author id and post id provided",
        parameters=[
            OpenApiParameter(name="visibility", description="visibilility of the post.", required=False, type=str),
            OpenApiParameter(name="title", description="title of the post.", requred=False, type=str),
            OpenApiParameter(name="description", description="the description of the post.", required=False, type=str),
            OpenApiParameter(name="contentType", description="the contentType of teh post.", required=False, type=str),
            OpenApiParameter(name="content", description="content of the post.", required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(description="Post updated succesfully", response=PostSerializer),
            400: OpenApiResponse(description=""),
            404: OpenApiResponse(description="User or Post are not found"),
            405: OpenApiResponse(descriptoin="Method not allowed"),
        }
    ) 
    @action(detail=False, methods=["PUT"])
    def update_post(self, request, user_id, post_id):
        """
        Updates the post requested
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who created the posts.
            post_id: The id of the post object.
            
        Returns:
            JsonResponce containing updated post 
        """
        if request.user.is_authenticated and user_id == request.PUT.get("user_id"):
            # Unsure the post and user exist
            user = get_object_or_404(User, id=user_id)
            post = get_object_or_404(Post, id=post_id)

            # Get the request contents
            post_type = request.POST.get("visibility")
            post_title = request.POST.get("title")
            post_id = request.POST.get("id")
            post_description = request.get("description")
            contentType_description = request.get("contentType")
            content_description = request.get("content")
            post_published = request.get("published")

            request.method = "GET"
            user_viewset = UserViewSet()
            response = user_viewset.retrieve(request, pk=user_id)
            author_data = json.loads(response.content)

            comments_viewset = CommentViewSet()
            response = comments_viewset.retrieve(request, pk=post_id)
            comments_data = json.loads(response.content)

            likes_viewset = LikeViewSet()
            response = likes_viewset.retrieve(request, pk=post_id)
            likes_data = json.loads(response.content)

            # Construct the post object to return in the responce
            if post_type in ["PUBLIC", "FRIENDS", "UNLISTED", "DELETED"]:
                postObject = {
                    "type": "post",
                    "title": post_title,
                    "id": post_id,
                    "description": post_description,
                    "contentType": contentType_description,
                    "content": content_description,
                    "author": {
                        "type": "author",
                        "id": author_data["id"],
                        "page": author_data["page"],
                        "host": author_data["host"],
                        "displayName": author_data["displayName"],
                        "github": author_data["github"],
                        "profileImage": author_data["profileImage"]
                    },
                    "comments":{
                        "type": "comments",
                        "page": comments_data["page"],
                        "id": comments_data["id"],
                        "page_number": comments_data["page_number"],
                        "size": comments_data["size"],
                        "count": comments_data["count"],
                        "src": comments_data["src"]
                    },
                    "likes": {
                        "types": "likes",
                        "page": likes_data["page"],
                        "id": likes_data["id"],
                        "page_number": likes_data["page_number"],
                        "size": likes_data["size"],
                        "count": likes_data["count"],
                        "src": likes_data["src"]
                    },
                    "published": post_published,
                    "visibility": post_type,
                }

                return JsonResponse(postObject, status=200)

            else:
                return JsonResponse({"error": "post visibility invalid"}, status=400)

        else:
            return JsonResponse({"error":"User is not authenticated"}, status=401)


    @extend_schema(
        summary="Get the recent posts made by an author",
        description="Retrieves the most recent posts made by an author based on the user ID, with optional pagination.",
        parameters=[
            OpenApiParameter(name="page", description="Page number for pagination.", required=False, type=int),
            OpenApiParameter(name="size", description="Number of posts per page.", required=False, type=int),
            OpenApiParameter(name="user_id", description="The id of the request user.", required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(description="Successfully retrieved all posts."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @api_view(["GET"])
    def get_posts(self, request, author_id):
        """
        Gets all the posts of a user.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the author who created the posts.

        Returns:
            JsonResponse containing the post objects.
        """
        page = request.GET.get("page")
        size = request.GET.get("size")
        request_user = request.GET.get("user_id")

        if page is None:
            page = 1 # Default page is 1

        if size is None:
            size = 10 # Default size is 50

        user = get_object_or_404(User, id=author_id)

        user_viewset = UserViewSet() 
        response = user_viewset.retrieve(request, pk=author_id)
        author_data = json.loads(response.content)
        
        if request.user.is_authenticated:
            posts = Post.objects.filter(Q(user=user, visibility="PUBLIC") | Q(user=user, visibility="FRIENDS") | Q(user=user, visibility="UNLISTED")).latest('published')
            if request_user == author_id or check_friendship(request, request_user, author_id):
                # Authenticated locally as an author or Authenticated locally as a friend
                # Paginate posts based on size
                posts_paginator = Paginator(posts, size)

                page_posts = posts_paginator.page(page)
                
                filtered_posts_attributes = []

                for post in page_posts:
                    post_id = post.id
                    comments_viewset = CommentViewSet()
                    response = comments_viewset.retrieve(request, pk=post_id)
                    comments_data = json.loads(response.content)

                    likes_viewset = LikeViewSet()
                    response = likes_viewset.retrieve(request, pk=post_id)
                    likes_data = json.loads(response.content)

                    postObject = {
                        "type": "post",
                        "title": post.title,
                        "id": post.id,
                        "description": post.description,
                        "contentType": post.contentType,
                        "content": post.content,
                        "author": {
                            "type": "author",
                            "id": author_data["id"],
                            "page": author_data["page"],
                            "host": author_data["host"],
                            "displayName": author_data["displayName"],
                            "github": author_data["github"],
                            "profileImage": author_data["profileImage"],
                        },
                        "comments": {
                            "type": "comments",
                            "page": comments_data["page"],
                            "id": comments_data["id"],
                            "page_number": comments_data["page_number"],
                            "size": comments_data["size"],
                            "count": comments_data["count"],
                            "src": comments_data["src"]
                        },
                        "likes": {
                            "types": "likes",
                            "page": likes_data["page"],
                            "id": likes_data["id"],
                            "page_number": likes_data["page_number"],
                            "size": likes_data["size"],
                            "count": likes_data["count"],
                            "src": likes_data["src"]
                        },
                        "published": post.published,
                        "visibility": post.visibility,
                    }

                    filtered_posts_attributes.append(postObject)

                return JsonResponse(filtered_posts_attributes, status=200)

        # Not authenticated (only view public posts)
        posts = Post.objects.filter(Q(user=user, visibility="PUBLIC")).latest('published')

        # Paginate posts based on size
        posts_paginator = Paginator(posts, size)

        page_posts = posts_paginator.page(page)
        
        filtered_posts_attributes = []

        for post in page_posts:
            post_id = post.id
            comments_viewset = CommentViewSet()
            response = comments_viewset.retrieve(request, pk=post_id)
            comments_data = json.loads(response.content)

            likes_viewset = LikeViewSet()
            response = likes_viewset.retrieve(request, pk=post_id)
            likes_data = json.loads(response.content)

            postObject = {
                "type": "post",
                "title": post.title,
                "id": post.id,
                "description": post.description,
                "contentType": post.contentType,
                "content": post.content,
                "author": {
                    "type": "author",
                    "id": author_data["id"],
                    "page": author_data["page"],
                    "host": author_data["host"],
                    "displayName": author_data["displayName"],
                    "github": author_data["github"],
                    "profileImage": author_data["profileImage"],
                },
                "comments": {
                    "type": "comments",
                    "page": comments_data["page"],
                    "id": comments_data["id"],
                    "page_number": comments_data["page_number"],
                    "size": comments_data["size"],
                    "count": comments_data["count"],
                    "src": comments_data["src"]
                },
                "likes": {
                    "types": "likes",
                    "page": likes_data["page"],
                    "id": likes_data["id"],
                    "page_number": likes_data["page_number"],
                    "size": likes_data["size"],
                    "count": likes_data["count"],
                    "src": likes_data["src"]
                },
                "published": post.published,
                "visibility": post.visibility,
            }

            filtered_posts_attributes.append(postObject)

        return JsonResponse(filtered_posts_attributes, status=200)
