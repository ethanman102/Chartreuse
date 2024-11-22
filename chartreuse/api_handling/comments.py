import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated

from ..models import User, Like, Post, Follow, Comment
from .users import UserSerializer, UserViewSet
from .likes import LikeSerializer, LikesSerializer, LikeViewSet
from .friends import FriendsViewSet
from urllib.parse import unquote
from ..views import checkIfRequestAuthenticated
from rest_framework.permissions import AllowAny

class CommentSerializer(serializers.Serializer):
    type = serializers.CharField(default="comment")
    author = UserSerializer
    comment = serializers.CharField()
    contentType = serializers.CharField()
    dateCreated = serializers.DateTimeField()
    id = serializers.URLField()
    post = serializers.URLField()
    likes = LikesSerializer()

    class Meta:
        fields = ['type', 'author', 'comment', 'contentType', 'published', 'id', 'post', 'likes']

class CommentsSerializer(serializers.Serializer):
    type = serializers.CharField(default="comments")
    page = serializers.URLField()
    id = serializers.URLField()
    page_number = serializers.IntegerField()
    size = serializers.IntegerField()
    src = CommentSerializer(many=True)

class CommentViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = CommentSerializer
    # authentication_classes = []

    @extend_schema(
        summary="Adds a comment on a post",
        description=(
            "Adds a comment on a post based on the provided post url"
            "\n\n**When to use:** Use this endpoint to add a comment to an existing post by providing the `user_id` (post author) and `post_id` (post being commented on) in the URL, along with the comment content in the request body."
            "\n\n**How to use:** Send a POST request with `content` and `contentType` as parameters, and the `user_id` and `post_id` in the URL."
            "\n\n**Why to use:** This API allows users to interact with posts by commenting, which can enhance engagement on the platform."
            "\n\n**Why not to use:** If the post does not exist or if the comment parameters are incorrect."
        ),
        parameters=[
            OpenApiParameter(name="content", description="The comment content.", required=False, type=str),
            OpenApiParameter(name="contentType", description="The comments content type.", required=False, type=str),
            OpenApiParameter(name="id", description="The post url id", required=True, type=str),
        ],
        responses={
            201: OpenApiResponse(description="Comment added successfully.", response=CommentSerializer),
            400: OpenApiResponse(
                description="Incorrect request body.",
                response=inline_serializer(
                    name="BadRequestResponse",
                    fields={"error": serializers.CharField(default="Incorrect request body")}
                )
            ),
            401: OpenApiResponse(
                description="User is not authenticated.",
                response=inline_serializer(
                    name="UnauthorizedResponse",
                    fields={"error": serializers.CharField(default="User is not authenticated.")}
                )
            ),
            404: OpenApiResponse(
                description="User not found.",
                response=inline_serializer(
                    name="NotFoundResponse",
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
        },
    )
    @action(detail=False, methods=["POST"])
    def create_comment(self, request, user_id, post_id=None):
        """
        Adds a comment on a post.
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the post author whos post is being commented on.
            post_id: The id of the post being commented on
            
        Returns:
            JsonResponce containing the comment object.  
        """
        checkIfRequestAuthenticated(request)
            
        decoded_author_id = unquote(user_id)

        if not post_id:
            # Get the post URL from the request body
            post_id = request.POST.get('id')
            if not post_id:
                return JsonResponse({"error": "Post URL is required"}, status=400)
        
        decoded_post_url = unquote(post_id)
        
        # Get the user commenting on the post
        decoded_commenter = unquote(request.user.user.url_id)
        user_commenting = get_object_or_404(User, url_id=decoded_commenter)

        post = get_object_or_404(Post, url_id=decoded_post_url, user=decoded_author_id)
        post_visibility = post.visibility

        # check post visibillity permission
        if post_visibility != "PUBLIC" and post_visibility != "UNLISTED" or (post_visibility == "FRIENDS" and FriendsViewSet().check_friendship(request, user_id, request.user.user.id).status_code != 200):
            return JsonResponse({"error": "User does not have permission to comment on this post"}, status=401)

        comment_text = request.POST.get('comment', '')
        content_type = request.POST.get('contentType', 'text/markdown')

        # User get_or_creat to simplify checking if the user already commented on the post
        comment = Comment(
            user=user_commenting,
            post=post,
            comment=comment_text,
            contentType=content_type,
        )
        
        comment.save()

        # get the comment authors details
        user_viewset = UserViewSet()
        user_response = user_viewset.retrieve(request, pk=decoded_commenter)

        if user_response.status_code != 200:
            return JsonResponse({"error": "Failed to retrieve user details."}, status=user_response.status_code)
        
        user_data = json.loads(user_response.content)

        # construct the comment (no likes are included for now since the comment was just created)
        comment_object = {
            "type": "comment",
            "author": {
                "type": "author",
                "id": user_data["id"],
                "page": user_data["page"],
                "host": user_data["host"],
                "displayName": user_data["displayName"],
                "github": user_data["github"],
                "profileImage": user_data["profileImage"],
            },
            "comment": comment_text,
            "contentType": content_type,
            "published": comment.dateCreated,
            "id": comment.url_id,
            "post": post.url_id,
        }

        return JsonResponse(comment_object, status=201)
    


    @extend_schema(
            summary="Deletes a comment on a post",
            description=(
                "Deletes a comment on a post based on the provided comment id"
                "\n\n**When to use:** Use this endpoint to remove a comment that was previously added to a post by providing the `comment_id` in the URL."
                "\n\n**How to use:** Send a DELETE request with the `comment_id` in the URL to specify which comment should be removed."
                "\n\n**Why to use:** This API is useful for managing user-generated content, allowing users or admins to delete comments when necessary."
                "\n\n**Why not to use:** If the `comment_id` does not exist or if the user lacks authorization to delete the comment."
            ),
            responses={
                200: OpenApiResponse(description="Comment removed successfully.", response=CommentSerializer),
                401: OpenApiResponse(
                    description="User is not authenticated.",
                    response=inline_serializer(
                        name="UnauthorizedResponse",
                        fields={"error": serializers.CharField(default="User is not authenticated.")}
                    )
                ),
                404: OpenApiResponse(
                    description="Comment not found.",
                    response=inline_serializer(
                        name="NotFoundResponse",
                        fields={"error": serializers.CharField(default="Comment not found.")}
                    )
                ),
                405: OpenApiResponse(
                    description="Method not allowed.",
                    response=inline_serializer(
                        name="MethodNotAllowedResponse",
                        fields={"error": serializers.CharField(default="Method not allowed.")}
                    )
                ),
            },
    )
    @action(detail=False, methods=["DELETE"])
    def delete_comment(self, request, comment_id):
        """
        Adds a comment on a post.
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            comment_id: the url id of the comment being removed
            
        Returns:
            JsonResponce containing the comment object.  
        """
        checkIfRequestAuthenticated(request)

        # Get the comment   
        comment = Comment.objects.filter(url_id = unquote(comment_id)).first()
        if not comment:
            return JsonResponse({"error": "Comment not found."}, status=404)
    
        # get the comment authors details
        request.method = "GET"
        user_viewset = UserViewSet()
        user_response = user_viewset.retrieve(request, pk=comment.user.url_id)

        if user_response.status_code != 200:
            return JsonResponse({"error": "Failed to retrieve user details."}, status=user_response.status_code)
        
        user_data = json.loads(user_response.content)

        like_viewset = LikeViewSet()
        response = like_viewset.get_comment_likes(request, comment.user.url_id, comment.post.url_id, comment_id)
        like_data = json.loads(response.content)

        # construct the comment (no likes are included for now since the comment was just created)
        comment_object = {
            "type": "comment",
            "author": {
                "type": "author",
                "id": user_data["id"],
                "page": user_data["page"],
                "host": user_data["host"],
                "displayName": user_data["displayName"],
                "github": user_data["github"],
                "profileImage": user_data["profileImage"],
            },
            "comment": comment.comment,
            "contentType": comment.contentType,
            "published": comment.dateCreated,
            "id": comment.url_id,
            "post": comment.post.url_id,
            "likes": {
                "type":"likes",
                "page": like_data["page"],
                "id": like_data["id"],
                "page_number": like_data["page_number"],
                "size": like_data["size"],
                "count": like_data["count"],
                "src": like_data["src"],
            }
        }

        # Delete the comment
        comment.delete()

        return JsonResponse(comment_object, status=200)
        

    @extend_schema(
        summary="Get all comments on a post",
        description=(
            "Fetches all comments for a given post, optionally supporting pagination parameters to manage the number of comments per page and the page number."
            "\n\n**When to use:** Use this endpoint to retrieve all comments associated with a post by providing the `post_id` (required) and optionally, `size` and `page` parameters for pagination."
            "\n\n**How to use:** Send a GET request with the `post_id` in the URL and include optional `size` and `page` query parameters if pagination is desired."
            "\n\n**Why to use:** This API allows users to view all comments on a post, supporting pagination for efficient data handling in applications with high comment volumes."
            "\n\n**Why not to use:** If the post does not exist or if an invalid page or size parameter is provided."
        ),
        parameters=[
            OpenApiParameter(name="size", description="the size of the comments paginator", required=False, type=str),
            OpenApiParameter(name="page", description="the page number of the comments paginator", required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(description="List of comments retrieved successfully.", response=CommentsSerializer),
            404: OpenApiResponse(
                description="Post or User not found.",
                response=inline_serializer(
                    name="NotFoundResponse",
                    fields={"error": serializers.CharField(default="Post or User not found.")}
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
    def get_comments(self, request, post_id, user_id=None):
        """
        Gets the comments of a post
        
        Parameters:
            request: HttpRequest object containing the request and query parameters.
            user_id: The id of the post author whos post is being commented on.
            post_id: The id of the post.
            
        Returns:
            JsonResponce containing the response   
        """
        # Decoded the post id
        decoded_post_url = unquote(post_id)
        
        if user_id != None:
            decoded_author_id = unquote(user_id)

            # Get the author
            author = get_object_or_404(User, url_id=decoded_author_id)

            # Get the post
            post = get_object_or_404(Post, url_id=decoded_post_url, user=author)

        else:
            post = get_object_or_404(Post, url_id=decoded_post_url)
            user_id = post.user.url_id


        # Get all comments related to the post
        page_number = request.GET.get('page', 1)     # defualt value 1
        size = request.GET.get('size', 5)       # default value 5
        comments = Comment.objects.filter(post=post)
        paginator = Paginator(comments, size)  # Pagination
        page_comments = paginator.get_page(page_number)

        filtered_comment_attributes =[]

        for comment in page_comments:
            user_viewset = UserViewSet()
            response = user_viewset.retrieve(request, pk=comment.user.url_id)
            author_data = json.loads(response.content)

            like_viewset = LikeViewSet()
            response = like_viewset.get_comment_likes(request, user_id, post_id, comment.url_id)
            like_data = json.loads(response.content)

            comment_object = {
                "type": "comment",
                "author": {
                    "type": "author",
                    "id": author_data["id"],
                    "page": author_data["page"],
                    "host": author_data["host"],
                    "displayName": author_data["displayName"],
                    "profileImage": author_data["profileImage"],

                },
                "comment": comment.comment,
                "contentType": comment.contentType,
                "published": comment.dateCreated,
                "id": comment.url_id,
                "post": post.url_id,
                "likes": {
                    "type":"likes",
                    "page": like_data["page"],
                    "id": like_data["id"],
                    "page_number": like_data["page_number"],
                    "size": like_data["size"],
                    "count": like_data["count"],
                    "src": like_data["src"],
                }
            }

            filtered_comment_attributes.append(comment_object)

        comments_object = {
            "type": "comments",
            "page": post.url_id,
            "id": post.url_id + f"/comments",
            "page_number": page_number,
            "size": 5,
            "count": len(comments),
            "src": filtered_comment_attributes
        }

        return JsonResponse(comments_object, safe=False, status=200)

    

    @extend_schema(
        summary="Gets a specific comment from a user",
        description=(
            "Retrieves a specific comment object from a user based on the post id, user id, and remote comment id"
            "\n\n**When to use:** Use this endpoint to retrieve a unique comment on a post by providing the `comment_id` and `post_id`. Optionally, the `user_id` can be used to further specify the author."
            "\n\n**How to use:** Send a GET request with `comment_id` and `post_id` in the URL. The optional `user_id` parameter can help identify the author of the post if needed."
            "\n\n**Why to use:** This API is useful for retrieving a particular comment's details, enabling targeted access for comment management or display."
            "\n\n**Why not to use:** Do not use if the comment, user, or post does not exist, as this will result in a 404 response."
        ),
        responses={
            200: OpenApiResponse(description="Successfully retrieved comment.", response=CommentSerializer),
            404: OpenApiResponse(
                description="User, comment, or post not found.",
                response=inline_serializer(
                    name="NotFoundResponse",
                    fields={"error": serializers.CharField(default="User, comment, or post not found.")}
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
    @api_view(["GET"]) 
    def get_comment(request, comment_id, user_id=None, post_id=None):
        """
        Gets a specific comment object from a post
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who created the posts. (not required)
            post_id: The id of the post object. (not required)
            comment_id: the remote/local id of the comment

        Returns:
            JsonResponce containing the response   
        """
        decoded_comment_id = unquote(comment_id)
        
        if user_id == None or post_id == None:
            comment = get_object_or_404(Comment, url_id=decoded_comment_id)
            post_id = comment.post.url_id
            user_id = comment.post.user.url_id

        else:
            decoded_author_id = unquote(user_id)
            user = get_object_or_404(User, url_id=decoded_author_id)

            decoded_post_id = unquote(post_id)
            post = get_object_or_404(Post, url_id=decoded_post_id, user=user)

            comment = get_object_or_404(Comment, url_id=decoded_comment_id, post=post)

        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=comment.user.url_id)
        author_data = json.loads(response.content)

        like_viewset = LikeViewSet()
        response = like_viewset.get_comment_likes(request, user_id, post_id, comment_id)
        like_data = json.loads(response.content)

        comment_object = {
            "type": "comment",
            "author": {
                "type": "author",
                "id": author_data["id"],
                "page": author_data["page"],
                "host": author_data["host"],
                "displayName": author_data["displayName"],
                "github": author_data["github"],
                "profileImage": author_data["profileImage"]
            },
            "comment": comment.comment,
            "contentType": comment.contentType,
            "published": comment.dateCreated,
            "id": comment.id,
            "post": comment.post.id,
            "likes": {
                "type":"likes",
                "page": like_data["page"],
                "id": like_data["id"],
                "page_number": like_data["page_number"],
                "size": like_data["size"],
                "count": like_data["count"],
                "src": like_data["src"],
            }

        }
        return JsonResponse(comment_object, status=200)


    @extend_schema(
        summary="Gets the list of comments an author has made.",
        description=(
            "Retrieves a a paginated list of comment objects from a user based on the user id."
            "\n\n**When to use:** Use this endpoint to retrieve all comments made by a specific author. This is useful when tracking or displaying an author's activity across posts."
            "\n\n**How to use:** Send a GET request with the `user_id` in the URL, along with optional `size` and `page` query parameters to manage pagination."
            "\n\n**Why to use:** This API facilitates access to an author's comments, enabling efficient management and display of content created by a specific user."
            "\n\n**Why not to use:** Avoid using this if the specified author has no comments, or if the user ID is invalid, which will result in a 404 response."
        ),
        parameters=[
            OpenApiParameter(name="size", description="the size of the comments paginator", required=False, type=str),
            OpenApiParameter(name="page", description="the page number of the comments paginator", required=False, type=str),
        ],
        responses={
            200: OpenApiResponse(description="Successfully retrieved comments.", response=CommentsSerializer),
            404: OpenApiResponse(
                description="User, or comment not found.",
                response=inline_serializer(
                    name="NotFoundResponse",
                    fields={"error": serializers.CharField(default="User, or comment not found.")}
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
    def get_authors_comments(self, request, user_id):
        """
        Gets the list of comments an author has made.
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            user_id: The id of the user who created the comments.

        Returns:
            JsonResponce containing the response   
        """
        # get the paginator page and size (default size 1 and 10)
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 10)

        # get the author of the comments
        decoded_author_id = unquote(user_id)
        comment_author = get_object_or_404(User, url_id=decoded_author_id)

        # Get all the comments authored by the given user
        comments = Comment.objects.filter(user=comment_author)

        # Filter the comments based on visibility
        # not required since comments are local for right now 

        # Paginates likes based on the size
        comments_paginator = Paginator(comments, size)
        page_comments = comments_paginator.page(page)
        comments_src = []

        # Get the authors data
        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=decoded_author_id)
        author_data = json.loads(response.content)

        # Create the list of comments
        for comment in page_comments:
            like_viewset = LikeViewSet()
            response = like_viewset.get_comment_likes(request, user_id, comment.post.url_id, comment.url_id)
            like_data = json.loads(response.content)

            comments_src.append({
                "type": "comment",
                "author": {
                    "type": "author",
                    "id": author_data["id"],
                    "page": author_data["page"],
                    "host": author_data["host"],
                    "displayName": author_data["displayName"],
                    "github": author_data["github"],
                    "profileImage": author_data["profileImage"]
                },
                "comment": comment.comment,
                "contentType": comment.contentType,
                "published": comment.dateCreated,
                "id": comment.url_id,
                "post": comment.post.url_id,
                "likes": {
                    "type":"likes",
                    "page": like_data["page"],
                    "id": like_data["id"],
                    "page_number": like_data["page_number"],
                    "size": like_data["size"],
                    "count": like_data["count"],
                    "src": like_data["src"],
                }
            })   

        authors_comments = {
            "type": "comments",
            "page_number": page,
            "size": size,
            "count": len(comments),
            "src":comments_src
        }   

        return JsonResponse(authors_comments, status=200)