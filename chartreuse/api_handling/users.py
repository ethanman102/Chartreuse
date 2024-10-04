import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, extend_schema_view
from rest_framework import serializers
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .. import views
from ..models import User

class AuthorSerializer(serializers.Serializer):
    type = serializers.CharField(default="author")
    id = serializers.CharField()
    host = serializers.CharField()
    displayName = serializers.CharField()
    github = serializers.URLField(required=False, allow_null=True)
    profileImage = serializers.URLField(required=False, allow_null=True)
    page = serializers.CharField()

class AuthorsSerializer(serializers.Serializer):
    type = serializers.CharField(default="authors")
    authors = AuthorSerializer(many=True)

def get_users(request):
    '''
    Gets a paginated list of users based on the provided query parameters.

    Parameters:
        request: HttpRequest object containing the request and query parameters.

    Returns:
        JsonResponse containing the paginated list of users.
    '''
    if request.method == "GET":
        page = request.GET.get('page')
        size = request.GET.get('size')

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
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def user(request, user_id):
    '''
    Gets a user, updates a user, or deletes a user.

    Parameters:
        request: HttpRequest object containing the request with the user id.
        user_id: The id of the user to get, update, or delete

    Returns:
        JsonResponse containing the user. (optional)
    '''
    if request.method == "GET":
        user = get_object_or_404(User, pk=user_id)

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

    elif request.method == "PUT":
        user = get_object_or_404(User, pk=user_id)

        id = user.host + "authors/" + str(user.user.id)
        page = user.host + "authors/" + user.user.username

        put = json.loads(request.body.decode('utf-8'))

        displayName = put.get('displayName')
        github = put.get('github')
        profileImage = put.get('profileImage')
        username = put.get('username')

        if (displayName is not None):
            user.displayName = displayName
        
        if (github is not None):
            user.github = github
        
        if (profileImage is not None):
            user.profileImage = profileImage
        
        if (username is not None):
            user.user.username = username

        # Save the updated user
        user.save()

        return JsonResponse({
            "type": "author",
            "id": id,
            "host": user.host,
            "displayName": user.displayName,
            "github": user.github,
            "profileImage": user.profileImage,
            "page": page
        }, safe=False)
    
    elif request.method == "DELETE":
        user = get_object_or_404(User, pk=user_id)

        logged_in_user = request.user

        if logged_in_user != user.user:
            return JsonResponse({"error": "You do not have permission to delete this user."}, status=403)

        user.delete()

        return JsonResponse({"success": "User deleted successfully."}, status=200)
    
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def create_user(request):
    '''
    Creates a new user.

    Parameters:
        request: HttpRequest object containing the request with the user details.
    
    Returns:
        JsonResponse containing the newly created user.
    '''
    if request.method == "POST":
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        displayName = request.POST.get('displayName')
        github = request.POST.get('github')
        profileImage = request.POST.get('profileImage')
        username = request.POST.get('username')
        password = request.POST.get('password')
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

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def login_user(request):
    '''
    Logs in a user.

    Parameters:
        request: HttpRequest object containing the request with the user details.
    
    Returns:
        JsonResponse containing the user details.
    '''
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({"error": "Username and password are required."}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"success": "User logged in successfully."}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials."}, status=400)
    
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)