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
from urllib.parse import unquote

class CommentSerializer(serializers.Serializer):
    type = serializers.CharField(default="comment")
    author = UserSerializer
    comment = serializers.CharField()
    contentType = serializers.CharField()
    published = serializers.DateTimeField()
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
            responses={
                200: OpenApiResponse(description="Comment added successfully.", response=CommentSerializer),
                400: OpenApiResponse(description="Comment already exists."),
                401: OpenApiResponse(description="User is not authenticated."),
                404: OpenApiResponse(description="User not found."),
                405: OpenApiResponse(description="Method not allowed."),
            }
    )
    @action(detail=False, methods=["POST"])
    def add_comment(self, request, post_author_id):
        """
        Adds a comment on a post.
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            post_author_id: The id of the post author whos post is being commented on.
            
        Returns:
            JsonResponce containing the comment object.  
        """
        decoded_author_id = unquote(post_author_id)

        try:
            post = Post.objects.get(id=request.data.get('post_id'), user__url_id=decoded_author_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404) 

        user = request.user
        comment_text = request.data.get('comment', '')
        content_type = request.data.get('contentType', 'text/markdown')

        comment = Comment.objects.create(
            user=user,
            post=post,
            comment=comment_text,
            commentType=content_type,
            username=user.displayName,
            password=request.data.get('password')
        )

        comment_serializer = CommentSerializer(comment)

        return JsonResponse(comment_serializer.data, status=201)
        
    @extend_schema(
        summary="Get all comments on a post",
        description="Fetch all comments on a post",
        responses={
            200: OpenApiResponse(description="List of comments retrieved successfully.", response=CommentsSerializer),
            404: OpenApiResponse(description="Post not found."),
        }
    )
    @action(detail=False, methods=["GET"])
    def get_comments(self, request, post_author_id):
        """
        Gets the comments of a post
        
        Parameters:
            request: HttpRequest object containing the request and query parameters.
            post_author_id: The id of the post author whos post is being commented on.
            
        Returns:
            JsonResponce containing the response   
        """
        if request.method == "GET":
            decoded_author_id = unquote(post_author_id)

            try:
                post = Post.objects.get(id=post_id, user__url_id=decoded_author_id)
            except Post.DoesNotExist:
                return JsonResponse({"error": "Post not found."}, status=404)

            # Get all comments related to the post
            comments = Comment.objects.filter(post=post)
            paginator = Paginator(comments, 10)  # Pagination
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            comments_serializer = CommentsSerializer({
                'type': 'comments',
                'page': page_obj.number,
                'id': post.url_id,
                'page_number': page_obj.number,
                'size': paginator.per_page,
                'src': page_obj.object_list,
            })

            return JsonResponse(comments_serializer.data, safe=False, status=200)

        else:
            return JsonResponse({"error": "Method not allowed."}, status=405)
    

    @extend_schema(
        summary="Gets a specific comment from a user",
        description="Retrieves a specific comment object from a user based on the post id, user id, and remote comment id",
        responses={
            200: OpenApiResponse(description="Successfully retrieved comment.", response=CommentSerializer),
            404: OpenApiResponse(description="User or comment or post not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @api_view(["GET"])
    def get_comment(request, post_author_id, post_id, remote_comment_id):
        """
        Gets a specific comment object from a post
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            post_author_id: The id of the user who is commenting on the posts.
            post_id: The id of the post object.
            remote_comment_id: the id of the remote comment id

        Returns:
            JsonResponce containing the response   
        """
        if request.method == "GET":
            decoded_author_id = unquote(post_author_id)
            decoded_post_id = unquote(post_id)

            try:
                post = Post.objects.get(id=decoded_post_id, user__url_id=decoded_author_id)
            except Post.DoesNotExist:
                return JsonResponse({"error": "Post not found."}, status=404)

            try:
                comment = Comment.objects.get(id=remote_comment_id, post=post)
            except Comment.DoesNotExist:
                return JsonResponse({"error": "Comment not found."}, status=404)

            comment_serializer = CommentSerializer(comment)
            return JsonResponse(comment_serializer.data, status=200)

        else:
            return JsonResponse({"error": "Method not allowed."}, status=405)
        


