import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.decorators import action, api_view
from .. import views
from ..models import User
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'host', 'displayName', 'github', 'profileImage']
    
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

    def validate_user(self, value):
        # You can add more validation rules for the username here
        username = value.get('username')
        if not username:
            raise serializers.ValidationError("Username cannot be empty.")
        return value
    
class UsersSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="authors")
    authors = UserSerializer(many=True)
    
    class Meta:
        model = User
        fields = ['type', 'authors']

class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get a list of users",
        description=("Gets a paginated list of users based on the provided query parameters (page and size)."),
        parameters=[
            OpenApiParameter(name='page', type=int, description="Page number for pagination (Default is 1)."),
            OpenApiParameter(name='size', type=int, description="Number of users per page (Default is 50)."),
        ],
        responses={
            200: OpenApiResponse( response=UsersSerializer(), description="A paginated list of users."),
        }
    )
    def list(self, request):
        '''
        Gets a paginated list of users based on the provided query parameters.

        Parameters:
            request: rest_framework object containing the request and query parameters.

        Returns:
            JsonResponse containing the paginated list of users.
        '''
        page = request.data.get('page')
        size = request.data.get('size')

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
            id = user.host + "authors/" + str(user.user.id)
            page = user.host + "authors/" + user.user.username

            filtered_user_attributes.append({
                "type": "author",
                "id": id,
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
        description=("Retrieves a user by their ID. Use this endpoint to get detailed information about a specific user."),
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="User details.",
            ),
            404: OpenApiResponse(
                description="User not found."
            )
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
        user = get_object_or_404(User, pk=pk)

        id = user.host + "authors/" + str(user.user.id)
        page = user.host + "authors/" + user.user.username

        # We only want to return the required fields
        return JsonResponse({
            "type": "author",
            "id": id,
            "host": user.host,
            "displayName": user.displayName,
            "github": user.github,
            "profileImage": user.profileImage,
            "page": page
        }, safe=False)

    @extend_schema(
        summary="Update a user",
        description=("Updates an existing user based on provided user details. "
                     "Use this endpoint to modify user attributes."),
        request=UserSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Updated user details.",
            ),
            404: OpenApiResponse(description="User not found."),
            403: OpenApiResponse(description="Permission denied."),
            400: OpenApiResponse(description="Invalid data."),
        }
    )
    def update(self, request, pk=None):
        if request.user.is_authenticated:
            user = get_object_or_404(User, pk=pk)

            id = user.host + "authors/" + str(user.user.id)
            page = user.host + "authors/" + user.user.username

            data = json.loads(request.body.decode('utf-8'))

            serializer = UserSerializer(instance=user, data=data, partial=True)

            # Save the updated user
            if serializer.is_valid():
                # If valid, save the updates
                serializer.save()
            
            else:
                return JsonResponse(serializer.errors, status=400)

            return JsonResponse({
                "type": "author",
                "id": id,
                "host": user.host,
                "displayName": user.displayName,
                "github": user.github,
                "profileImage": user.profileImage,
                "page": page
            }, safe=False)
        else:
            return Response({"error": "Permission denied."}, status=403)
        
    @extend_schema(
        summary="Delete a user",
        description=("Deletes an existing user based on the provided user ID. "),
        responses={
            200: OpenApiResponse(description="User deleted successfully."),
            404: OpenApiResponse(description="User not found."),
            403: OpenApiResponse(description="You do not have permission to delete this user."),
        }
    )
    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)

        logged_in_user = request.user

        if logged_in_user != user.user:
            return Response({"error": "You do not have permission to delete this user."}, status=403)

        user.delete()
        return Response({"success": "User deleted successfully."}, status=200)

    @extend_schema(
        summary="Create a new user",
        description=("Creates a new user with the provided details."),
        request=UserSerializer,
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Newly created user details."),
            400: OpenApiResponse(description="Username already exists."),
        }
    )
    def create(self, request):
        '''
        Creates a new user.

        Parameters:
            request: rest_framework object containing the request with the user details.
        
        Returns:
            JsonResponse containing the newly created user.
        '''
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

        user = User.objects.create(
            displayName = displayName,
            github = github,
            profileImage = profileImage,
            host = host,
            user=authUser
        )

        # Save the user
        user.save()

        id = user.host + "authors/" + str(user.user.id)
        page = user.host + "authors/" + user.user.username

        return JsonResponse({
            "type": "author",
            "id": id,
            "host": user.host,
            "displayName": user.displayName,
            "github": user.github,
            "profileImage": user.profileImage,
            "page": page
        }, safe=False, status=200)

    @extend_schema(
        summary="Login a user",
        description=("Logs in a user based on the provided user details."),
        responses={
            200: OpenApiResponse(description="User logged in successfully."),
            400: OpenApiResponse(description="Invalid credentials."),
            400: OpenApiResponse(description="Username and password are required."),
        }
    )
    @action(detail=False, methods=["POST"])
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
