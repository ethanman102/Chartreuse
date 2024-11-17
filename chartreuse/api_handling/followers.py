from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import User, FollowRequest, Follow
from django.contrib.auth.decorators import login_required
import json
from urllib.parse import unquote
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiTypes, inline_serializer
from django.core.paginator import Paginator
from ..views import checkIfRequestAuthenticated
from rest_framework.permissions import AllowAny

class FollowerSerializer(serializers.Serializer):
    type = serializers.CharField(default="author")
    id = serializers.URLField()
    host = serializers.URLField()
    displayName = serializers.CharField()
    page = serializers.URLField()
    github = serializers.URLField()
    profileImage = serializers.URLField()

    class Meta:
        fields = ['type', 'id', 'host', 'displayName', 'page', 'github', 'profileImage']

class FollowersSerializer(serializers.Serializer):
    type = serializers.CharField(default="followers")
    followers = FollowerSerializer(many=True)

    class Meta:
        fields = ['type', 'followers']


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = FollowerSerializer
    authentication_classes = []

    @extend_schema(
        summary="Add a follower",
        description=(
            "Adds a new follower to the author's list based on the provided author IDs."
            "\n\n**When to use:** Use this endpoint when an author wants to follow another author"
            "\n\n**How to use:** Send a POST request with the `author_id` (current author) and `foreign_author_id` (the author who will follow)."
            "\n\n**Why to use:** This API facilitates the creation of follow relationships between authors, useful in social applications."
            "\n\n**Why not to use:** If either author does not exist, or if the follow request is not properly structured, the request may fail."
        ),
        responses={
            201: OpenApiResponse(description="Follower added", response=FollowerSerializer),
            400: OpenApiResponse(
                description="Already a follower",
                response=inline_serializer(
                    name="AlreadyFollowerResponse",
                    fields={"message": serializers.CharField(default="Already a follower")}
                ),
            ),
            404: OpenApiResponse(
                description="Author not found.",
                response=inline_serializer(
                    name="AuthorNotFoundResponse",
                    fields={"message": serializers.CharField(default="Author not found")}
                ),
            ),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed")}
                ),
            ),
        }
    )
    @action(detail=False, methods=["POST"])
    def add_follower(self, request, author_id, foreign_author_id):
        '''
        Handles adding a follower.

        Parameters:
            request: HttpRequest object containing the request.
            author_id: The id of the current author.
            foreign_author_id: The id of the author who is becoming a follower

        Returns:
            JsonResponse with the success message
        '''
        checkIfRequestAuthenticated(request)

        # if not request.user.is_authenticated:
        #     return JsonResponse({"error": "User is not authenticated."}, status=401)

        if request.method == 'POST' or request.method == 'PUT':

            decoded_author_id = unquote(author_id)
            decoded_foreign_author_id = unquote(foreign_author_id)

            author = get_object_or_404(User, url_id=decoded_author_id)
            foreign_author = get_object_or_404(User, url_id=decoded_foreign_author_id)

            # Check if the user already follows the author
            if Follow.objects.filter(follower=foreign_author, followed=author).exists():
                return JsonResponse({"message": "Already a follower"}, status=400)

            # Create and save a follower object
            Follow.objects.create(follower=foreign_author, followed=author)
            return JsonResponse({"message": "Follower added"}, status=201)

        else:
            return JsonResponse({"error": "Method not allowed."}, status=405)

    @extend_schema(
        summary="Remove a follower",
        description=(
            "Removes an author from the follower list of another author based on the provided author IDs."
            "\n\n**When to use:** Use this endpoint when an author wants to unfollow another author."
            "\n\n**How to use:** Send a DELETE request with the `author_id` (current author) and `foreign_author_id` (the author to be unfollowed)."
            "\n\n**Why to use:** This API is useful in managing social relationships by allowing authors to remove followers."
            "\n\n**Why not to use:** If the authors do not exist or are not following each other, the request may fail."
        ),
        request=FollowerSerializer,
        responses={
            204: OpenApiResponse(
                description="Follower removed.",
                response=inline_serializer(
                    name="FollowerRemovedResponse",
                    fields={"message": serializers.CharField(default="Follower removed.")}
                ),
            ),
            400: OpenApiResponse(
                description="Not a follower.",
                response=inline_serializer(
                    name="NotFollowerResponse",
                    fields={"message": serializers.CharField(default="Not a follower.")}
                ),
            ),
            404: OpenApiResponse(
                description="Author not found.",
                response=inline_serializer(
                    name="AuthorNotFoundResponse",
                    fields={"message": serializers.CharField(default="Author not found")}
                ),
            ),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed")}
                ),
            ),
        }
    )
    @action(detail=False, methods=["DELETE"])
    def remove_follower(self, request, author_id, foreign_author_id):
        '''
        Handles unfollowing an author.

        Parameters:
            request: HttpRequest object containing the request.
            author_id: The id of the current author
            foreign_author_id: The id of the author to unfollow

        Returns:
            JsonResponse with success message.
        '''
        checkIfRequestAuthenticated(request)
        if request.method == 'DELETE':
            decoded_author_id = unquote(author_id)
            decoded_foreign_author_id = unquote(foreign_author_id)

            author = get_object_or_404(User, url_id=decoded_author_id)
            foreign_author = get_object_or_404(User, url_id=decoded_foreign_author_id)

            # Check if the user is following the author
            follow = Follow.objects.filter(follower=foreign_author, followed=author)

            if not follow.exists():
                return JsonResponse({"error": "Not a follower."}, status=400)

            # Remove the follower
            follow.delete()

            return JsonResponse({"message": "Follower removed."}, status=204)

        else:
            return JsonResponse({"error": "Method not allowed."}, status=405)

    @extend_schema(
        summary="Retrieve list of followers for a specific author",
        description=(
            "Retrieves the list of followers for an author based on the provided author ID."
            "\n\n**When to use:** Use this endpoint to fetch a list of all followers for a specific author."
            "\n\n**How to use:** Send a GET request with the `author_id` in the URL."
            "\n\n**Why to use:** This API helps in managing social relationships by fetching all followers of an author."
            "\n\n**Why not to use:** If the author ID is invalid or the author has no followers."
        ),
        request=FollowerSerializer,
        responses={
            200: OpenApiResponse(description="Successfully retrieved the list of followers.", response=FollowersSerializer),
            400: OpenApiResponse(
                description="Invalid request or missing parameters.",
                response=inline_serializer(
                    name="InvalidRequestResponse",
                    fields={"message": serializers.CharField(default="Invalid request or missing parameters.")}
                ),
            ),
            404: OpenApiResponse(
                description="Author not found.",
                response=inline_serializer(
                    name="AuthorNotFoundResponse",
                    fields={"message": serializers.CharField(default="Author not found")}
                ),
            ),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed")}
                ),
            ),
        }
    )
    @action(detail=False, methods=["GET"])
    def get_followers(self, request, author_id):
        '''
        Retrieves the list of followers for a specific author.

        Parameters:
            request: HttpRequest object containing the request.
            author_id: The id of the author whose followers are being retrieved.

        Returns:
            JsonResponse with the list of followers.
        '''
        decoded_author_id = unquote(author_id)

        # Fetch the author based on the provided author_id
        author = get_object_or_404(User, url_id=decoded_author_id)
        
        # Get all followers for the author
        followers = Follow.objects.filter(followed=author)

        followers_list = []

        # Create a list of follower details to be included in the response
        for follower in followers:
            user = follower.follower
            follower_attributes = [
                {
                    "type": "author",
                    "id": f"{user.host}authors/{user.user.id}",
                    "host": user.host,
                    "displayName": user.displayName,
                    "page": f"{user.host}authors/{user.url_id}",
                    "github": user.github,
                    "profileImage": user.profileImage
                }
            ]
            followers_list.append(follower_attributes)

        # Prepare the final response
        response = {
            "type": "followers",
            "followers": followers_list
        }

        return JsonResponse(response, status=200)

    @extend_schema(
        summary="Check if a specific author is a follower",
        description=(
            "Checks if a particular foreign author is following the specified author."
            "\n\n**When to use:** Use this endpoint to verify if a foreign author (by `foreign_author_id`) is following a particular author (by `author_id`)."
            "\n\n**How to use:** Send a GET request with both `author_id` and `foreign_author_id` in the URL to check the follower relationship."
            "\n\n**Why to use:** This API helps in checking social relationships, determining if one specific author follows another."
            "\n\n**Why not to use:** If the provided IDs are invalid or if no follower relationship exists."
        ),
        responses={
            200: OpenApiResponse(
                description="Is a follower",
                response=inline_serializer(
                    name="IsFollowerResponse",
                    fields={"message": serializers.CharField(default="Is a follower")}
                ),
            ),
            404: OpenApiResponse(
                description="Not a follower",
                response=inline_serializer(
                    name="NotFollowerResponse",
                    fields={"message": serializers.CharField(default="Not a follower")}
                ),
            ),
            405: OpenApiResponse(
                description="Method not allowed.",
                response=inline_serializer(
                    name="MethodNotAllowedResponse",
                    fields={"error": serializers.CharField(default="Method not allowed")}
                ),
            ),
        }
    )
    @action(detail=False, methods=["GET"])
    def is_follower(self, request, author_id, foreign_author_id):
        '''
        Checks if a particular author is a follower of current author

        Parameters:
            request: HttpRequest object containing the request.
            author_id: The id of the current author
            foreign_author_id: The id of the author to unfollow

        Returns:
            JsonResponse with success message.
        '''
        decoded_author_id = unquote(author_id)
        decoded_foreign_author_id = unquote(foreign_author_id)

        author = get_object_or_404(User, url_id=decoded_author_id)
        foreign_author = get_object_or_404(User, url_id=decoded_foreign_author_id)

        if Follow.objects.filter(follower=foreign_author, followed=author).exists():
            return JsonResponse({"message": "Is a follower"}, status=200)
        return JsonResponse({"message": "Not a follower"}, status=404)
