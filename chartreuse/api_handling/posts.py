import json

from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework import viewsets

from ..models import User, Post
from .users import UserSerializer, UserViewSet
from .comments import CommentViewSet
from .likes import LikeViewSet
from .likes import LikesSerializer
from .comments import CommentsSerializer
from urllib.parse import unquote
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from ..views import checkIfRequestAuthenticated, Host
from ..view import post_utils

def create_user_url_id(request, id):
    id = unquote(id)
    if id.find(":") != -1:
        return id
    else:
        # create the url id
        host = request.get_host()
        scheme = request.scheme
        url = f"{scheme}://{host}/chartreuse/api/authors/{id}"
        return url


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

class PostsSerializer(serializers.Serializer):
    type = serializers.CharField(default="posts")
    posts = PostSerializer(many=True)

    class Meta:
        fields = ['type', 'posts']

class PostViewSet(viewsets.ViewSet):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    @extend_schema(
        summary="Adds a post",
        description=(
            "Adds a post based on the on author URL"
            "\n\n**When to use:** Use this endpoint to allow an authenticated user to create a post."
            "\n\n**How to use:** Send a POST request with the necessary parameters, including the post's title, content, and optional visibility settings."
            "\n\n**Why to use:** This API is useful when users need to share content, such as articles, status updates, or other posts."
            "\n\n**Why not to use:** If the user is not authenticated, the post cannot be created, and this endpoint should not be used."
        ),
        request=PostSerializer,
        parameters=[
            OpenApiParameter(name="visibility", description="visibilility of the post.", required=False, type=str),
            OpenApiParameter(name="title", description="title of the post.", required=True, type=str),
            OpenApiParameter(name="description", description="the description of the post.", required=False, type=str),
            OpenApiParameter(name="contentType", description="the contentType of the post.", required=False, type=str),
            OpenApiParameter(name="content", description="content of the post.", required=True, type=str),
        ],
        responses = {
            201: OpenApiResponse(description="Post created successfully.", response=PostSerializer),
            400: OpenApiResponse(
                description="Request syntax invalid.",
                response=inline_serializer(
                    name="InvalidRequestResponse",
                    fields={"error": serializers.CharField(default="Request syntax invalid.")}
                )
            ),
            401: OpenApiResponse(
                description="User is not authenticated.",
                response=inline_serializer(
                    name="UnauthenticatedResponse",
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
    def create_post(self, request, user_id):
        """
        Creates a new post.
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is creating the post.
            
        Returns:
            JsonResponce containing the new post    
        """ 
        # DEBUG 
        print("Debug", user_id)

        user = User.objects.filter(url_id=user_id).first()

        # DEBUG
        print("Debug", user, user.host, Host.host)

        host = Host()

        # DEBUG
        print("Debug", host)

        if user is None:
            return JsonResponse({"error": "User not found."}, status=404)

        elif user.host != host.host:
            response = checkIfRequestAuthenticated(request)
            if response.status_code == 401:
                return response
            
        decoded_user_id = unquote(user_id)

        # Ensure the user creating the post is the current user
        author = User.objects.get(pk=decoded_user_id)

        post_type = request.POST.get("visibility") 
        if not post_type:
            post_type = "PUBLIC"

        post_title = request.POST.get("title")
        if not post_title:
            return JsonResponse({"error": "Post title is required."}, status=400)
        
        post_description = request.POST.get("description")
        contentType_description = request.POST.get("contentType")
        if not contentType_description:
            contentType_description = "text/plain"

        content_description = request.POST.get("content")
        if not content_description:
            return JsonResponse({"error": "Post content is required."}, status=400)

        # Create and save the post
        post = Post.objects.create(user=author, title=post_title, description=post_description, contentType=contentType_description, content=content_description, visibility=post_type)
        post.save()
        print(post.url_id,'FRIENDS POST URLID')
        post_utils.send_post_to_inbox(post.url_id)

        # get the author data
        request.method = "GET"
        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=user_id)
        author_data = json.loads(response.content)

        if response.status_code != 200:
            return JsonResponse({"error": "Failed to retrieve user details."}, status=response.status_code)

        # Construct the post object to return in the responce
        if post_type in ["PUBLIC", "FRIENDS", "UNLISTED", "DELETED"]:
            postObject = {
                "type": "post",
                "title": post_title,
                "id": post.url_id,
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
                "published": post.published,
                "visibility": post_type,
            }
            return JsonResponse(postObject, status=201)

        else:
            return JsonResponse({"error": "post visibliity invalid"}, status=400)

        
    @extend_schema(
        summary="Removes a post",
        description=(
            "Removes a post based on the provided post URL."
            "\n\n**When to use:** Use this endpoint to delete a post that the user has authored."
            "\n\n**How to use:** Send a DELETE request with the `post` parameter set to the URL of the post you wish to delete."
            "\n\n**Why to use:** This API is useful for users who want to remove their own posts from the platform."
            "\n\n**Why not to use:** If the post does not exist or if the user is not authenticated, the post cannot be deleted."
        ),
        request=PostSerializer,
        parameters=[
            OpenApiParameter(name="post", description="the post url.", required=True, type=str),
        ],
        responses={
            200: OpenApiResponse(
                description="Post deleted successfully.",
                response=inline_serializer(
                    name="PostDeletedResponse",
                    fields={"message": serializers.CharField(default="Post deleted successfully.")}
                )
            ),
            400: OpenApiResponse(
                description="Post does not exist.",
                response=inline_serializer(
                    name="PostDoesNotExistResponse",
                    fields={"error": serializers.CharField(default="Post does not exist.")}
                )
            ),
            401: OpenApiResponse(
                description="User not authenticated.",
                response=inline_serializer(
                    name="UnauthenticatedResponse",
                    fields={"error": serializers.CharField(default="User not authenticated.")}
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
    def remove_post(self, request, user_id, post_id):
        """
        Reassigns the status of a post to DELETED.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who is liking the post.

        Returns:
            JsonResponse containing the like object.
        """
        response = checkIfRequestAuthenticated(request)
        if response.status_code == 401:
            return response
        decoded_user_id = unquote(user_id)
        decoded_post_url = unquote(post_id)

        # Ensure the user deleting the post is the current user
        author = User.objects.get(pk=decoded_user_id)

        # Delete the post
        post = Post.objects.filter(user=author, url_id=decoded_post_url)[0]
        post.visibility = "DELETED"
        post.save()

        # get the post data
        request.method = "GET"
        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=decoded_user_id)
        author_data = json.loads(response.content)

        if response.status_code != 200:
            return JsonResponse({"error": "Failed to retrieve user details."}, status=response.status_code)

        comments_viewset = CommentViewSet()
        response = comments_viewset.get_comments(request, post_id=post.url_id, user_id=user_id)
        comments_data = json.loads(response.content)

        likes_viewset = LikeViewSet()
        response = likes_viewset.get_post_likes(request, user_id=post.user.url_id, post_id=post.url_id)
        likes_data = json.loads(response.content)

        # Construct the post object to return in the responce
        postObject = {
            "type": "post",
            "title": post.title,
            "id": post.url_id,
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
                "page_number": likes_data["page_number"],
                "size": likes_data["size"],
                "count": likes_data["count"],
                "src": likes_data["src"]
            },
            "published": post.published,
            "visibility": post.visibility,
        }

        return JsonResponse(postObject, status=200)
        

    @extend_schema(
            summary="Gets a specific post from a user",
            description=(
                "Retrieves a specific post object from a user based on the user id and post id"
                "\n\n**When to use:** Use this endpoint to fetch details of a particular post authored by a specific user."
                "\n\n**How to use:** Send a GET request with the `user_id` and `post_id` as parameters in the URL."
                "\n\n**Why to use:** This API helps in retrieving the content and metadata of a post, useful for viewing posts in detail."
                "\n\n**Why not to use:** If the post is restricted to FRIENDS only and the user is not friends with the author, access will be denied."
            ),
            request=PostSerializer,
            parameters=[
            OpenApiParameter(name="user_id", description="The id of the user requesting the post.", required=False, type=str),
            OpenApiParameter(name="post_id", description="The ID of the post to retrieve (required).", required=False, type=str),
            ],
            responses={
                200: OpenApiResponse(description="Successfully retrieved post.", response=PostSerializer),
                400: OpenApiResponse(
                    description="This is a FRIENDS only post and user and author are not friends.",
                    response=inline_serializer(
                        name="FriendsOnlyPostResponse",
                        fields={"error": serializers.CharField(default="This is a FRIENDS only post and user and author are not friends.")}
                    )
                ),
                401: OpenApiResponse(
                    description="User is not authenticated.",
                    response=inline_serializer(
                        name="UnauthenticatedResponse",
                        fields={"error": serializers.CharField(default="User is not authenticated.")}
                    )
                ),
                404: OpenApiResponse(
                    description="Post does not exist.",
                    response=inline_serializer(
                        name="NotFoundResponse",
                        fields={"error": serializers.CharField(default="Post does not exist.")}
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
        decoded_user_id = unquote(user_id)
        decoded_post_id = unquote(post_id)

        author = User.objects.get(url_id=decoded_user_id)

        post = Post.objects.filter(user=author, url_id=decoded_post_id).first()

        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=user_id)
        author_data = json.loads(response.content)
    
        comments_viewset = CommentViewSet()
        response = comments_viewset.get_comments(request, post_id=post.url_id, user_id=user_id)
        comments_data = json.loads(response.content)

        likes_viewset = LikeViewSet()
        response = likes_viewset.get_post_likes(request, user_id=post.user.url_id, post_id=post.url_id)
        likes_data = json.loads(response.content)
    
        if post.visibility in ["PUBLIC", "UNLISTED", "DELETED"]:
            postObject = {
                "type": "post",
                "title": post.title,
                "id": post.url_id,
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
                    "page_number": comments_data["page_number"],
                    "size": comments_data["size"],
                    "count": comments_data["count"],
                    "src": comments_data["src"]
                },
                "likes": {
                    "types": "likes",
                    "page": likes_data["page"],
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
            postObject = {
                "type": "post",
                "title": post.title,
                "id": post.url_id,
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
                    # "id": likes_data["id"],
                    "page_number": likes_data["page_number"],
                    "size": likes_data["size"],
                    "count": likes_data["count"],
                    "src": likes_data["src"]
                },
                "published": post.published,
                "visibility": post.visibility,
            } 
        else:
            return JsonResponse({"error": "Post does not exist."}, status=404)
        
        return JsonResponse(postObject, status=200)

    @extend_schema(
        summary="Updates the post",
        description=(
            "Updates the post using the author id and post id provided"
            "\n\n**When to use:** Use this endpoint to modify an existing post's details, such as visibility, title, description, content type, and content."
            "\n\n**How to use:** Send a PATCH request with the `user_id`, `post_id`, and any fields you wish to update as parameters."
            "\n\n**Why to use:** This API allows authors to manage their posts effectively by updating essential information."
            "\n\n**Why not to use:** If the post does not exist or if the user is not authorized to modify the post, the update will fail."
        ),
        request=PostSerializer,
        parameters=[
            OpenApiParameter(name="visibility", description="visibilility of the post.", required=False, type=str),
            OpenApiParameter(name="title", description="title of the post.", required=False, type=str),
            OpenApiParameter(name="description", description="the description of the post.", required=False, type=str),
            OpenApiParameter(name="contentType", description="the contentType of teh post.", required=False, type=str),
            OpenApiParameter(name="content", description="content of the post.", required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(description="Post updated succesfully.", response=PostSerializer),
            400: OpenApiResponse(
                description="post visibility invalid",
                response=inline_serializer(
                    name="UserNotFoundResponse",
                    fields={"error": serializers.CharField(default="post visibility invalid")}
                )
            ),
            401: OpenApiResponse(
                description="User is not authenticated",
                response=inline_serializer(
                    name="UserNotAuthenticatedResponse",
                    fields={"error": serializers.CharField(default="User is not authenticated")}
                )
            ),
            404: OpenApiResponse(
                description="Post not found.",
                response=inline_serializer(
                    name="PostNotFoundResponse",
                    fields={"error": serializers.CharField(default="Post not found.")}
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
    def update(self, request, user_id, post_id):
        """
        Updates the post requested
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who created the posts.
            post_id: The id of the post object.
            
        Returns:
            JsonResponce containing updated post 
        """
        response = checkIfRequestAuthenticated(request)
        if response.status_code == 401:
            return response

        decoded_user_id = unquote(user_id)
        decoded_post_id = unquote(post_id)
        
        author = User.objects.get(url_id=decoded_user_id)
        post = Post.objects.filter(user=author, url_id=decoded_post_id)[0]

        # Get the request contents
        post_type = request.POST.get("visibility")
        if not post_type:
            post_type = post.type
        
        post_title = request.POST.get("title")
        if not post_title:
            post_title = post.title

        post_description = request.POST.get("description")
        if not post_description:
            post_description = post.decription

        post_contentType = request.POST.get("contentType")
        if not post_contentType:
            post_contentType = post.contentType

        post_content = request.POST.get("content")
        if not post_content:
            post_content = post.content

        request.method = "GET"
        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=user_id)
        author_data = json.loads(response.content)

        comments_viewset = CommentViewSet()
        response = comments_viewset.get_comments(request, post_id=post.url_id, user_id=user_id)
        comments_data = json.loads(response.content)

        likes_viewset = LikeViewSet()
        response = likes_viewset.get_post_likes(request, user_id=post.user.url_id, post_id=post.url_id)
        likes_data = json.loads(response.content)

        # Construct the post object to return in the responce
        if post_type in ["PUBLIC", "FRIENDS", "UNLISTED", "DELETED"]:
            postObject = {
                "type": "post",
                "title": post_title,
                "id": post.url_id,
                "description": post_description,
                "contentType": post_contentType,
                "content": post_content,
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
                    "page_number": likes_data["page_number"],
                    "size": likes_data["size"],
                    "count": likes_data["count"],
                    "src": likes_data["src"]
                },
                "published": post.published,
                "visibility": post_type,
            }

            return JsonResponse(postObject, status=200)

        else:
            return JsonResponse({"error": "post visibility invalid"}, status=400)


    @extend_schema(
        summary="Get the recent posts made by an author",
        description=(
            "Retrieves the most recent posts made by an author based on the user ID, with optional pagination."
            "\n\n**When to use:** Use this endpoint to fetch the latest posts from a specific author."
            "\n\n**How to use:** Send a GET request with the `user_id`, along with optional pagination parameters `page` and `size`."
            "\n\n**Why to use:** This API helps in fetching recent content from an author, which is useful for displaying updates or new posts."
            "\n\n**Why not to use:** If the author does not exist or if the request is not properly formatted, the retrieval may fail."
        ),
        request=UserSerializer,
        parameters=[
            OpenApiParameter(name="page", description="Page number for pagination.", required=False, type=int),
            OpenApiParameter(name="size", description="Number of posts per page.", required=False, type=int),
            OpenApiParameter(name="user_id", description="The id of the request user.", required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(description="Successfully retrieved all posts.", response=PostsSerializer),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed.")}
                )
            ),
        }
    )
    def get_posts(self, request, user_id):
        """
        Gets all the posts of a user.

        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the author who created the posts.

        Returns:
            JsonResponse containing the post objects.
        """
        checkIfRequestAuthenticated(request)
        decoded_author_id = create_user_url_id(request, user_id)

        page = request.GET.get("page")
        size = request.GET.get("size")

        if page is None:
            page = 1  # Default page is 1
        else:
            page = int(page)

        if size is None:
            size = 10  # Default size is 10
        else:
            size = int(size)

        user = get_object_or_404(User, pk=decoded_author_id)

        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=decoded_author_id)
        author_data = json.loads(response.content)

        if request.user.is_authenticated:
            posts = Post.objects.filter(
                Q(user=user, visibility="PUBLIC") |
                Q(user=user, visibility="FRIENDS") |
                Q(user=user, visibility="UNLISTED")
            ).order_by('-published')
        else:
            posts = Post.objects.filter(
                Q(user=user, visibility="PUBLIC")
            ).order_by('-published')

        posts_paginator = Paginator(posts, size)

        page_posts = posts_paginator.page(page)
        
        filtered_posts_attributes = []

        for post in page_posts:

            comments_viewset = CommentViewSet()
            response = comments_viewset.get_comments(request, post_id=post.url_id, user_id=user_id)
            comments_data = json.loads(response.content)

            likes_viewset = LikeViewSet()
            response = likes_viewset.get_post_likes(request, user_id=post.user.url_id, post_id=post.url_id)
            likes_data = json.loads(response.content)

            postObject = {
                "type": "post",
                "title": post.title,
                "id": post.url_id,
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
                    "page_number": likes_data["page_number"],
                    "size": likes_data["size"],
                    "count": likes_data["count"],
                    "src": likes_data["src"]
                },
                "published": post.published,
                "visibility": post.visibility,
            }

            filtered_posts_attributes.append(postObject)
        
        posts = {
            "type": "posts",
            "page_number": page,
            "size": size,
            "count": posts_paginator.count,
            "src": filtered_posts_attributes
        }

        return JsonResponse(posts, status=200, safe=False)