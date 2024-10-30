import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated

from ..models import User, Like, Post, Follow, Comment
from .users import UserSerializer, UserViewSet
from .likes import LikeSerializer, LikesSerializer, LikeViewSet
from .friends import FriendsViewSet
from urllib.parse import unquote

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
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    @extend_schema(
            summary="Adds a comment on a post",
            description="Adds a comment on a post based on the provided post url",
            parameters=[
                OpenApiParameter(name="content", description="The comment content.", required=False, type=str),
                OpenApiParameter(name="contentType", description="The comments content type.", required=False, type=str),
                # OpenApiParameter(name="post", description="The post url id", required=True, type=str),
            ],
            responses={
                200: OpenApiResponse(description="Comment added successfully.", response=CommentSerializer),
                400: OpenApiResponse(description="Comment already exists or incorrect request body"),
                401: OpenApiResponse(description="User is not authenticated."),
                404: OpenApiResponse(description="User not found."),
                405: OpenApiResponse(description="Method not allowed."),
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
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
            
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
        if post_visibility != "PUBLIC" and post_visibility != "UNLISTED" or (post_visibility == "FREINDS" and FriendsViewSet().check_friendship(request, user_id, request.user.user.id).status_code != 200):
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
            description="Deletes a comment on a post based on the provided comment id",
            responses={
                200: OpenApiResponse(description="Comment removed successfully.", response=CommentSerializer),
                401: OpenApiResponse(description="User is not authenticated."),
                404: OpenApiResponse(description="Comment not found."),
                405: OpenApiResponse(description="Method not allowed."),
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
        if not request.user.is_authenticated:
            return JsonResponse({"error": "User is not authenticated."}, status=401)

        # Get the comment   
        comment = Comment.objects.filter(url_id = unquote(comment_id)).first()
    
        # get the comment authors details
        request.method = "GET"
        user_viewset = UserViewSet()
        user_response = user_viewset.retrieve(request, pk=comment.user.url_id)

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
            "comment": comment.comment,
            "contentType": comment.contentType,
            "published": comment.dateCreated,
            "id": comment.url_id,
            "post": comment.post.url_id,
        }

        # Delete the comment
        comment.delete()

        return JsonResponse(comment_object, status=200)
        

    @extend_schema(
        summary="Get all comments on a post",
        description="Fetch all comments on a post",
        responses={
            200: OpenApiResponse(description="List of comments retrieved successfully.", response=CommentsSerializer),
            404: OpenApiResponse(description="Post not found."),
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
                    "type": "likes",
                    "page": None
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
        description="Retrieves a specific comment object from a user based on the post id, user id, and remote comment id",
        responses={
            200: OpenApiResponse(description="Successfully retrieved comment.", response=CommentSerializer),
            404: OpenApiResponse(description="User, comment, or post not found."),
            405: OpenApiResponse(description="Method not allowed."),
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

        else:
            decoded_author_id = unquote(user_id)
            user = get_object_or_404(User, url_id=decoded_author_id)

            decoded_post_id = unquote(post_id)
            post = get_object_or_404(Post, url_id=decoded_post_id, user=user)

            comment = get_object_or_404(Comment, url_id=decoded_comment_id, post=post)

        user_viewset = UserViewSet()
        response = user_viewset.retrieve(request, pk=comment.user.url_id)
        author_data = json.loads(response.content)

        # like_viewset = LikeViewSet()
        # response = like_viewset.get_comment_likes(request, user_id, post_id, comment_id)
        # like_data = json.loads(response.content)

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
            "id": comment.url_id,
            "post": comment.post.url_id

        }
        return JsonResponse(comment_object, status=200)


    @extend_schema(
        summary="Gets the list of comments an author has made.",
        description="Retrieves a a paginated list of comment objects from a user based on the user id.",
        responses={
            200: OpenApiResponse(description="Successfully retrieved comments.", response=CommentSerializer),
            404: OpenApiResponse(description="User, or comment not found"),
            405: OpenApiResponse(description="Method not allowed."),
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
            })   

        authors_comments = {
            "src":comments_src
        }   

        return JsonResponse(authors_comments, status=200)