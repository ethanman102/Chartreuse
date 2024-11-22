import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from urllib.parse import unquote
import requests
import regex as re
from ..views import checkIfRequestAuthenticated

from .. import views
from ..models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class UserSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="author")
    id = serializers.URLField()
    displayName = serializers.CharField()
    host = serializers.URLField()
    github = serializers.URLField()
    profileImage = serializers.URLField()
    page = serializers.URLField()

    class Meta:
        model = User
        fields = ['type', 'id', 'displayName', 'host', 'github', 'profileImage', 'page', 'dateCreated']

    def validate_displayName(self, value):
        if not value:
            raise serializers.ValidationError("Display name cannot be empty.")
        return value

    def validate_github(self, value):
        if not value.startswith("http"):
            raise serializers.ValidationError("GitHub URL must start with 'http'.")
        return value

    def validate_profileImage(self, value):
        if not value.startswith("http"):
            raise serializers.ValidationError("Profile image URL must start with 'http'.")
        return value

class UsersSerializer(serializers.Serializer):
    type = serializers.CharField(default="authors")
    authors = UserSerializer(many=True)

    class Meta:
        fields = ['type', 'authors']

class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    

    @extend_schema(
        summary="Get a list of users",
        description=(
            "Gets a paginated list of users based on the provided query parameters (page and size)."
            "\n\n**When to use:** Use this endpoint when you need to display a list of all users."
            "\n\n**How to use:** Send a GET request to this endpoint. You can use pagination by specifying the 'page' and 'size' parameters."
            "\n\n**Why to use:** This endpoint allows you to view all users, useful for user management features."
            "\n\n**Why not to use:** Avoid using this endpoint for individual user details; use the specific user endpoint instead."),
        parameters=[
            OpenApiParameter(name='page', type=int, description="Page number for pagination (Default is 1)."),
            OpenApiParameter(name='size', type=int, description="Number of users per page (Default is 50)."),
        ],
        responses={
            200: OpenApiResponse( 
                response=UsersSerializer(), description="A paginated list of users.",
                   
            ),
            404: OpenApiResponse(
                response=None,
                description="No users found."
            ),
        }
    )
    
    def list(self, request):
        '''
        Gets a paginated list of users based on the provided query parameters. 
        This will only get users who are registered on the current host.

        Parameters:
            request: rest_framework object containing the request and query parameters.

        Returns:
            JsonResponse containing the paginated list of users.
        '''
        auth_response = checkIfRequestAuthenticated(request)
       
        if auth_response.status_code == 401:
            return auth_response

        page = request.query_params.get('page', 1)
        size = request.query_params.get('size', 50)

        if (page is None):
            page = 1 # Default page is 1

        if (size is None):
            size = 50 # Default size is 50
        
        # Gets all the users
        users = User.objects.all()

        # Paginates users based on the size
        user_paginator = Paginator(users, size)

        page_users = user_paginator.page(page)

        # Since we have some additional fields, we only want to return the required ones
        filtered_user_attributes = []
        for user in page_users:
            page = user.host + "authors/" + user.url_id

            filtered_user_attributes.append({
                "type": "author",
                "id": user.url_id,
                "host": user.host,
                "displayName": user.displayName,
                "github": user.github,
                "profileImage": user.profileImage,
                "page": page
            })

        authors = {
            "type": "authors",
            "authors": filtered_user_attributes
        }

        return JsonResponse(authors, safe=False)

    @extend_schema(
        summary="Get a specific user",
        description=(
            "Retrieves a user by their ID."
            "\n\n**When to use:** Use this endpoint to fetch information about a specific user."
            "\n\n**How to use:** Send a GET request with the user ID as a path parameter."
            "\n\n**Why to use:** This endpoint is useful when you need details about a specific user, such as their display name, GitHub URL, or profile image."
            "\n\n**Why not to use:** Avoid using this endpoint to list multiple users. Use the user list endpoint instead."
        ),
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="User details.",
            ),
            404: OpenApiResponse(
                description="User not found.",
                response=inline_serializer(
                    name="UserNotFoundResponse",
                    fields={"message": serializers.CharField(default="User not found.")}
                )
            ),
        }
    )
    def retrieve(self, request, pk=None):
        '''
        Gets a user.

        Parameters:
            request: rest_framework object containing the request with the user id.
            user_id: The id of the user to get, update, or delete

        Returns:
            JsonResponse containing the user.
        '''
        decoded_user_id = unquote(pk)
        
        # case where the user is on the current host
        user = get_object_or_404(User, pk=decoded_user_id)
        page = user.host + "/authors/" + user.url_id

        # We only want to return the required fields
        return JsonResponse({
            "type": "author",
            "id": user.id,
            "host": user.host,
            "displayName": user.displayName,
            "github": user.github,
            "profileImage": user.profileImage,
            "page": page
        }, safe=False)

    @extend_schema(
        summary="Update a user",
        description=(
            "Updates an existing user based on provided user details."
            "\n\n**When to use:** Use this endpoint to modify an existing user's details, such as their display name, GitHub link, or profile image."
            "\n\n**How to use:** Send a PUT request with the new user data in the request body, and the user ID as a path parameter."
            "\n\n**Why to use:** This endpoint is crucial for user profile management, allowing users to update their own information."
            "\n\n**Why not to use:** Do not use this endpoint to create new users; use the user creation endpoint for that."
        ),
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Updated user details.",
            ),
            404: OpenApiResponse(
                description="User not found.",
                response=inline_serializer(
                    name="UserNotFoundResponse",
                    fields={"message": serializers.CharField(default="User not found.")}
                )
            ),
            401: OpenApiResponse(
                description="Permission denied.",
                response=inline_serializer(
                    name="PermissionDeniedResponse",
                    fields={"error": serializers.CharField(default="Permission denied.")}
                )
            ),
            400: OpenApiResponse(
                description="Invalid data.",
                response=inline_serializer(
                    name="InvalidDataResponse",
                    fields={"error": serializers.CharField(default="Invalid data.")}
                )
            ),
        }
    )
    def update(self, request, pk=None):
        auth_response = checkIfRequestAuthenticated(request)

        if auth_response.status_code == 401:
            return auth_response

        decoded_user_id = unquote(pk)
        host = get_host_from_id(decoded_user_id)

        data = json.loads(request.body.decode('utf-8'))

        if(host != views.Host.host):
            # if the user is not on the current host, we need to get the user from the remote host
            api_url = host + "api/authors/" + pk
            response = requests.put(api_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})

            response.raise_for_status()
            response_data = response.json()

            return JsonResponse(response_data, safe=False)
        else:
            # case where the user is on the current host
            user = get_object_or_404(User, pk=decoded_user_id)
            page = user.host + "/authors/" + user.url_id

            serializer = UserSerializer(instance=user, data=data, partial=True)

            # Save the updated user
            if serializer.is_valid():
                # If valid, save the updates
                serializer.save()
            
            else:
                return JsonResponse(serializer.errors, status=400)

            return JsonResponse({
                "type": "author",
                "id": user.url_id,
                "host": user.host,
                "displayName": user.displayName,
                "github": user.github,
                "profileImage": user.profileImage,
                "page": page
            }, safe=False)
        
    @extend_schema(
        summary="Delete a user",
        description=(
            "Deletes an existing user based on the provided user ID. "
            "\n\n**When to use:** Use this endpoint to remove a user permanently."
            "\n\n**How to use:** Send a DELETE request with the user ID as a path parameter."
            "\n\n**Why to use:** This endpoint is useful for user account removal, typically used in admin dashboards or user account deletion flows."
            "\n\n**Why not to use:** Be cautious when using this endpoint as it will permanently delete the user data."
        ),
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                description="User deleted successfully.",
                response=inline_serializer(
                    name="UserDeletedResponse",
                    fields={"message": serializers.CharField(default="User deleted successfully.")}
                )
            ),
            404: OpenApiResponse(
                description="User not found.",
                response=inline_serializer(
                    name="UserNotFoundResponse",
                    fields={"message": serializers.CharField(default="User not found.")}
                )
            ),
            401: OpenApiResponse(
                description="You do not have permission to delete this user.",
                response=inline_serializer(
                    name="PermissionDeniedResponse",
                    fields={"error": serializers.CharField(default="You do not have permission to delete this user.")}
                )
            ),
        }
    )
    def destroy(self, request, pk=None):
        auth_response = checkIfRequestAuthenticated(request)
        if auth_response.status_code == 401:
            return auth_response
        
        decoded_user_id = unquote(pk)

        host = get_host_from_id(decoded_user_id)
        
        if(host != views.Host.host):
            # if the user is not on the current host, we need to get the user from the remote host
            api_url = host + "api/authors/" + decoded_user_id
            response = requests.delete(api_url)

            # Raise an exception if the request failed
            response.raise_for_status()

            return Response({"success": "User deleted successfully."}, status=200)
        else:
            logged_in_user = request.user
            user = get_object_or_404(User, pk=decoded_user_id)

            if logged_in_user != user.user:
                return Response({"error": "You do not have permission to delete this user."}, status=401)
            # case where the user is on the current host
            user.delete()
            return Response({"success": "User deleted successfully."}, status=200)

    @extend_schema(
        summary="Create a new user",
        description=(
            "Creates a new user with the provided details."
            "\n\n**When to use:** Use this endpoint when a new user wants to sign up for the platform."
            "\n\n**How to use:** Send a POST request with the user details in the request body."
            "\n\n**Why to use:** This endpoint facilitates user registration, enabling users to access platform features."
            "\n\n**Why not to use:** Do not use this endpoint for updating existing users; use the update endpoint instead."
            ),
        request=UserSerializer,
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Newly created user details."),
            400: OpenApiResponse(
                description="Username already exists.",
                response=inline_serializer(
                    name="UsernameAlreadyExistsResponse",
                    fields={"error": serializers.CharField(default="Username already exists.")}
                )
            ),
        }
    )
    def create(self, request):
        '''
        Creates a new user on the current host.

        Parameters:
            request: rest_framework object containing the request with the user details.
        
        Returns:
            JsonResponse containing the newly created user.
        '''
        auth_response = checkIfRequestAuthenticated(request)
        if auth_response.status_code == 401:
            return auth_response
        
        firstName = request.data.get('firstName')
        lastName = request.data.get('lastName')
        displayName = request.data.get('displayName')
        github = request.data.get('github')
        profileImage = request.data.get('profileImage')
        username = request.data.get('username')
        password = request.data.get('password')
        host = views.Host.host
    
        authUser = AuthUser.objects.filter(username=username)

        if authUser.exists():
            return JsonResponse({"error": "Username already exists."}, status=400)

        # Validate password
        try:
            validate_password(password)
        except ValidationError as e:
            return JsonResponse({"error": e.messages}, status=400)
    
        authUser = AuthUser.objects.create(
            first_name = firstName,
            last_name = lastName,
            username = username,
        )

        authUser.set_password(password)
        authUser.save()

        id = host + "api/authors/" + str(authUser.id)

        user = User.objects.create(
            url_id = id,
            displayName = displayName,
            github = github,
            profileImage = profileImage,
            host = host,
            user=authUser
        )

        # Save the user
        user.save()

        page = user.host + "/authors/" + user.url_id

        return JsonResponse({
            "type": "author",
            "id": user.url_id,
            "host": user.host,
            "displayName": user.displayName,
            "github": user.github,
            "profileImage": user.profileImage,
            "page": page
        }, safe=False, status=200)

    @extend_schema(
        summary="Login a user",
        description=(
            "Logs in a user based on the provided user details."
            "\n\n**When to use:** Use this endpoint when an author wants to access their account."
            "\n\n**How to use:** Send a POST request with the required `username` and `password` fields in the request body."
            "\n\n**Why to use:** This API enables users to authenticate and access their accounts securely."
            "\n\n**Why not to use:** If the credentials are invalid or missing, the login attempt will fail."
        ),
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                description="User logged in successfully.",
                response=inline_serializer(
                    name="LoginSuccessResponse",
                    fields={"message": serializers.CharField(default="User logged in successfully.")}
                )
            ),
            400: OpenApiResponse(
                description="Invalid credentials.",
                response=inline_serializer(
                    name="InvalidCredentialsResponse",
                    fields={"error": serializers.CharField(default="Invalid credentials.")}
                )
            ),
            400: OpenApiResponse(
                description="Username and password are required.",
                response=inline_serializer(
                    name="MissingCredentialsResponse",
                    fields={"error": serializers.CharField(default="Username and password are required.")}
                )
            ),
        }
    )
    @api_view(["POST"])
    def login_user(request):
        '''
        Logs in a user.

        Parameters:
            request: rest_framework object containing the request with the user details.
        
        Returns:
            JsonResponse containing the user details.
        '''
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return JsonResponse({"error": "Username and password are required."}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"success": "User logged in successfully."}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials."}, status=400)

def get_host_from_id(user_id):
    '''
    Gets the host from the user id.

    Parameters:
        user_id: The user id to extract the host from.

    Returns:
        The host of the user.
    '''
    pattern = r'(https?:\/\/[^\/]+\/)'
    match = re.match(pattern, user_id)
    return match.group(1)