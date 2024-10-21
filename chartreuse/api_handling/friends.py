from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import Follow, User
from urllib.parse import unquote
from rest_framework import serializers, viewsets
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator

class FriendSerializer(serializers.Serializer):
    type = serializers.CharField(default="author")
    id = serializers.URLField()
    host = serializers.URLField()
    displayName = serializers.CharField()
    page = serializers.URLField()
    github = serializers.URLField()
    profileImage = serializers.URLField()

    class Meta:
        fields = ['type', 'id', 'host', 'displayName', 'page', 'github', 'profileImage']

class FriendsSerializer(serializers.Serializer):
    type = serializers.CharField(default="friends")
    friends = FriendSerializer(many=True)

    class Meta:
        fields = ['type', 'friends']

class FriendsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer

    @extend_schema(
        summary="Retrieve list of friends for a specific author",
        description=(
            "Retrieves the list of friends (mutual followers) for an author based on the provided author ID."
            "\n\n**When to use:** Use this endpoint to fetch a list of all friends of a specific author. A friend is defined as an author who follows and is followed by the same author."
            "\n\n**How to use:** Send a GET request with the `author_id` in the URL."
            "\n\n**Why to use:** This API helps in managing mutual relationships, fetching friends of an author."
            "\n\n**Why not to use:** If the author has no friends or invalid author ID is provided."
        ),
        responses={
            200: OpenApiResponse(description="Successfully retrieved the list of friends.", response=FriendsSerializer),
            404: OpenApiResponse(description="Author not found."),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @action(detail=False, methods=["GET"])
    def get_friends(self, request, author_id):
        '''
        Retrieves the list of friends for a specific author.

        Parameters:
            request: HttpRequest object containing the request.
            author_id: The id of the author whose friends are being retrieved.

        Returns:
            JsonResponse with the list of friends.
        '''
        decoded_author_id = unquote(author_id)
        author = get_object_or_404(User, url_id=decoded_author_id)

        # Get the followers of the author
        followers = Follow.objects.filter(followed=author).values_list('follower', flat=True)

        # Get the authors that the current author follows
        following = Follow.objects.filter(follower=author).values_list('followed', flat=True)

        friends = User.objects.filter(url_id__in=followers).filter(url_id__in=following)

        friends_list = []

        for friend in friends:
            friend_attributes = {
                "type": "author",
                "id": f"{friend.host}authors/{friend.user.id}",
                "host": friend.host,
                "displayName": friend.displayName,
                "page": f"{friend.host}authors/{friend.url_id}",
                "github": friend.github,
                "profileImage": friend.profileImage
            }
            friends_list.append(friend_attributes)


        response = {
            "type": "friends",
            "friends": friends_list
        }

        return JsonResponse(response, status=200)

    @extend_schema(
        summary="Check if two authors are friends (mutual followers)",
        description=(
            "Checks whether two authors (identified by their author IDs) are mutual followers (friends). "
            "A friend is defined as someone who both follows and is followed by the same author."
            "\n\n**When to use:** Use this endpoint when you need to verify the friendship (mutual following) between two authors."
            "\n\n**How to use:** Send a GET request with the `author_id` (the current author) and `foreign_author_id` (the author to check friendship with)."
            "\n\n**Why to use:** This API helps determine if two authors have a mutual following relationship."
            "\n\n**Why not to use:** Don't use this to check a one-way relationship."
        ),
        responses={
            200: OpenApiResponse(description="Authors are friends"),
            404: OpenApiResponse(description="Authors are not friends"),
            405: OpenApiResponse(description="Method not allowed."),
        }
    )
    @action(detail=False, methods=["GET"])
    def check_friendship(self, request, author_id, foreign_author_id):
        '''
        Checks if two authors are friends (mutual followers).

        Parameters:
            request: HttpRequest object containing the request.
            author_id: The id of the current author
            foreign_author_id: The id of the author to check friendship with

        Returns:
            JsonResponse with a message indicating friendship status.
        '''
        decoded_author_id = unquote(author_id)
        decoded_foreign_author_id = unquote(foreign_author_id)

        author = get_object_or_404(User, url_id=decoded_author_id)
        foreign_author = get_object_or_404(User, url_id=decoded_foreign_author_id)

        # Check if the current user follows the author and vice versa
        if (Follow.objects.filter(follower=author, followed=foreign_author).exists() and
            Follow.objects.filter(follower=foreign_author, followed=author).exists()):
            return JsonResponse({"message": "Authors are friends"}, status=200)

        return JsonResponse({"message": "Authors are not friends"}, status=404)