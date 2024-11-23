from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import User, FollowRequest, Follow
from django.contrib.auth.decorators import login_required
from urllib.parse import unquote
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, inline_serializer
from django.core.paginator import Paginator
from ..views import checkIfRequestAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication

class ActorSerializer(serializers.Serializer):
    type = serializers.CharField(default="author")
    id = serializers.URLField()
    host = serializers.URLField()
    displayName = serializers.CharField()
    page = serializers.URLField()
    github = serializers.URLField()
    profileImage = serializers.URLField()

    class Meta:
        fields = ['type', 'id', 'host', 'displayName', 'page', 'github', 'profileImage']

class ObjectSerializer(serializers.Serializer):
    type = serializers.CharField(default="author")
    id = serializers.URLField()
    host = serializers.URLField()
    displayName = serializers.CharField()
    page = serializers.URLField()
    github = serializers.URLField()
    profileImage = serializers.URLField()

    class Meta:
        fields = ['type', 'id', 'host', 'displayName', 'page', 'github', 'profileImage']

class FollowRequestSerializer(serializers.Serializer):
    type = serializers.CharField(default="follow")
    summary = serializers.CharField()
    actor = ActorSerializer()
    object = ObjectSerializer()

    class Meta:
        fields = ['type', 'summary', 'actor', 'object']

class FollowRequestsSerializer(serializers.Serializer):
    type = serializers.CharField(default="follow_requests")
    follow_requests = FollowRequestSerializer(many=True)

    class Meta:
        fields = ['type', 'follow_requests']

class FollowRequestViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = FollowRequestSerializer
    authentication_classes = [SessionAuthentication]

    @extend_schema(
        summary="Send a follow request",
        description=(
            "Sends a follow request to a specified author based on the provided author ID."
            "\n\n**When to use:** Use this endpoint when an author wants to request to follow another author."
            "\n\n**How to use:** Send a POST request with the `author_id` of the author to whom the follow request is being sent."
            "\n\n**Why to use:** This API enables authors to initiate follow requests, enhancing social interaction in the application."
            "\n\n**Why not to use:** If the target author does not exist, or if the follow request is improperly structured, the request may fail."
        ),
        request=ObjectSerializer,
        responses={
            200: OpenApiResponse(description="Follow request sent.", response=FollowRequestSerializer),
            400: OpenApiResponse(
                description="Follow request already sent.",
                response=inline_serializer(
                    name="FollowRequestAlreadySentResponse",
                    fields={"message": serializers.CharField(default="Follow request already sent.")}
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
    def send_follow_request(self, request, author_id):
        '''
        Handles sending a follow request to an author.

        Parameters:
            request: HttpRequest object containing the request.
            author_id: The id of the author to send the follow request to.

        Returns:
            JsonResponse with the follow request details.
        '''
        if request.method == 'POST':
            response = checkIfRequestAuthenticated(request)
            if response.status_code == 401:
                return response

            decoded_author_id = unquote(author_id)

            current_user = User.objects.get(user=request.user)
            author = get_object_or_404(User, url_id=decoded_author_id)

            # Check if a follow request already exists
            if FollowRequest.objects.filter(requester=current_user, requestee=author).exists():
                return JsonResponse({"error": "Follow request already sent."}, status=400)

            # Create and save a follow request
            follow_request = FollowRequest(requester=current_user, requestee=author)
            follow_request.save()

            return JsonResponse({"message": "Follow request sent."}, status=200)

        else:
            return JsonResponse({"error": "Method not allowed."}, status=405)

    @extend_schema(
        summary="Accept a follow request",
        description=(
            "Accepts a follow request from another author based on the provided request ID."
            "\n\n**When to use:** Use this endpoint when an author wants to accept a follow request from another author."
            "\n\n**How to use:** Send a POST request with the `request_id` of the follow request to be accepted."
            "\n\n**Why to use:** This API facilitates the acceptance of follow requests, enhancing the social connectivity within the application."
            "\n\n**Why not to use:** If the follow request does not exist or has already been accepted/declined, the request may fail."
        ),
        request=FollowRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="Follow request accepted.",
                response=inline_serializer(
                    name="FollowRequestAcceptedResponse",
                    fields={"message": serializers.CharField(default="Follow request accepted.")}
                ),
            ),
            404: OpenApiResponse(
                description="Follow request not found.",
                response=inline_serializer(
                    name="FollowRequestNotFoundResponse",
                    fields={"message": serializers.CharField(default="Follow request not found.")}
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
    def accept_follow_request(self, request, request_id):
        '''
        Accepts a follow request.

        Parameters:
            request: HttpRequest object containing the request.
            request_id: The id of the follow request to accept.

        Returns:
            JsonResponse with success message.
        '''
        if request.method == 'POST':
            response = checkIfRequestAuthenticated(request)
            if response.status_code == 401:
                return response
            follow_request = get_object_or_404(FollowRequest, id=request_id)

            # Create a follower object
            follower = Follow(follower=follow_request.requester, followed=follow_request.requestee)
            follower.save()

            # Delete the follow request
            follow_request.delete()

            return JsonResponse({"message": "Follow request accepted."}, status=200)

        else:
            return JsonResponse({"error": "Method not allowed."}, status=405)

    @extend_schema(
        summary="Reject a follow request",
        description=(
            "Rejects a follow request from another author based on the provided follow request ID."
            "\n\n**When to use:** Use this endpoint when an author wants to decline a follow request from another author."
            "\n\n**How to use:** Send a POST request with the `request_id` of the follow request to be rejected."
            "\n\n**Why to use:** This API facilitates the management of follow requests, allowing authors to maintain control over their connections."
            "\n\n**Why not to use:** If the follow request does not exist or has already been accepted/declined, the request may fail."
        ),
        request=FollowRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="Follow request rejected.",
                response=inline_serializer(
                    name="FollowRequestRejectedResponse",
                    fields={"message": serializers.CharField(default="Follow request rejected.")}
                ),
            ),
            404: OpenApiResponse(
                description="Follow request not found.",
                response=inline_serializer(
                    name="FollowRequestNotFoundResponse",
                    fields={"message": serializers.CharField(default="Follow request not found.")}
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
    def reject_follow_request(self, request, request_id):
        '''
        Rejects a follow request.

        Parameters:
            request: HttpRequest object containing the request.
            request_id: The id of the follow request to reject.

        Returns:
            JsonResponse with success message.
        '''
        response = checkIfRequestAuthenticated(request)
        if response.status_code == 401:
            return response
        if request.method == 'DELETE':
            follow_request = get_object_or_404(FollowRequest, id=request_id)

            # Delete the follow request
            follow_request.delete()

            return JsonResponse({"message": "Follow request rejected."}, status=200)

        else:
            return JsonResponse({"error": "Method not allowed."}, status=405)


    @extend_schema(
        summary="Get follow requests for a user",
        description=(
            "Retrieves the list of pending follow requests for the logged-in user."
            "\n\n**When to use:** Use this endpoint when you want to check the follow requests that are awaiting your approval."
            "\n\n**How to use:** Send a GET request to retrieve the list of follow requests."
            "\n\n**Why to use:** This API allows authors to manage their incoming follow requests and decide whom to connect with."
            "\n\n**Why not to use:** If the user is not authenticated, or if there are no pending follow requests, the request may not yield the expected results."
        ),
        request=ActorSerializer,
        responses={
            200: OpenApiResponse(description="List of follow requests retrieved successfully.", response=FollowRequestsSerializer),
            401: OpenApiResponse(
                description="Unauthorized access. User must be logged in.",
                response=inline_serializer(
                    name="UnauthorizedAccessResponse",
                    fields={"error": serializers.CharField(default="Unauthorized access. User must be logged in.")}
                ),
            ),
            404: OpenApiResponse(
                description="No follow requests found for the logged-in user.",
                response=inline_serializer(
                    name="NoFollowRequestsFoundResponse",
                    fields={"message": serializers.CharField(default="No follow requests found for the logged-in user.")}
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
    def get_follow_requests(self, request):
        '''
        Retrieves the list of pending follow requests for the logged-in user.

        Parameters:
            request: HttpRequest object containing the request.

        Returns:
            JsonResponse with the list of follow requests.
        '''
        author = User.objects.get(user=request.user)

        follow_requests = FollowRequest.objects.filter(requestee=author, approved=False)

        requests_list = [
            {
                "type": "follow",
                "summary": f"{follow_request.requester.displayName} wants to follow {follow_request.requestee.displayName}",
                "actor": {
                    "type": "author",
                    "id": f"{follow_request.requester.host}/authors/{follow_request.requester.user.id}",
                    "host": follow_request.requester.host,
                    "displayName": follow_request.requester.displayName,
                    "page": f"{follow_request.requester.host}authors/{follow_request.requester.url_id}",
                    "github": follow_request.requester.github,
                    "profileImage": follow_request.requester.profileImage
                },
                "object": {
                    "type": "author",
                    "id": f"{follow_request.requestee.host}/authors/{follow_request.requestee.user.id}",
                    "host": follow_request.requestee.host,
                    "displayName": follow_request.requestee.displayName,
                    "page": f"{follow_request.requestee.host}authors/{follow_request.requestee.url_id}",
                    "github": follow_request.requestee.github,
                    "profileImage": follow_request.requestee.profileImage
                }
            }
            for follow_request in follow_requests
        ]

        return JsonResponse({"follow_requests": requests_list}, status=200)
