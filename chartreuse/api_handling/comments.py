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
                400: OpenApiResponse(description="Comment already exists or incorrect request body"),
                401: OpenApiResponse(description="User is not authenticated."),
                404: OpenApiResponse(description="User not found."),
                405: OpenApiResponse(description="Method not allowed."),
            }
    )
    @action(detail=False, methods=["POST"])
    def create_comment(self, request, post_author_id):
        """
        Adds a comment on a post.
        
        Parameters:
            request: rest_framework object containing the request and query parameters.
            post_author_id: The id of the post author whos post is being commented on.
            
        Returns:
            JsonResponce containing the comment object.  
        """
        if (not request.user.is_authenticated):
            return JsonResponse({"error": "User is not authenticated."}, status=401)
            
        decoded_author_id = unquote(post_author_id)

        # Get the post URL from the request body
        post_url = request.POST.get('post')
        if not post_url:
            return JsonResponse({"error": "Post URL is required"}, status=400)
        
        decoded_post_url = unquote(post_url)
        
        # Get the user commenting on the post
        decoded_commenter = unquote(request.user.user.url_id)
        user_commenting = get_object_or_404(User, url_id=decoded_commenter)

        post = get_object_or_404(Post, url_id=decoded_post_url, user=decoded_author_id)

        comment_text = request.data.get('comment', '')
        content_type = request.data.get('contentType', 'text/markdown')


        # User get_or_creat to simplify checking if the user already commented on the post
        comment, created = Comment.objects.get_or_create(
            user=user_commenting,
            post=post,
            comment=comment_text,
            commentType=content_type,
        )

        if not created:
            return JsonResponse({"error": "Comment already exists."}, status=400)
        
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
        


