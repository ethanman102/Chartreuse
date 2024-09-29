from django.http import JsonResponse
from django.core.paginator import Paginator
from ..models import User
from django.shortcuts import get_object_or_404
from .. import views
import json

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
            id = user.host + "authors/" + str(user.id)
            page = user.host + "authors/" + user.username

            filtered_user_attributes.append({
                "type": "author",
                "id": id,
                "host": user.host,
                "displayName": user.displayName,
                "github": user.github,
                "profileImage": user.profileImage,
                "page": page
            })

        return JsonResponse(filtered_user_attributes, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def user(request, user_id):
    '''
    Gets an user, updates an user, or deletes a user.

    Parameters:
        request: HttpRequest object containing the request with the user id.
        user_id: The id of the user to get, update, or delete

    Returns:
        JsonResponse containing the user. (optional)
    '''
    if request.method == "GET":
        user = get_object_or_404(User, pk=user_id)

        id = user.host + "authors/" + str(user.id)
        page = user.host + "authors/" + user.username

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

        id = user.host + "authors/" + str(user.id)
        page = user.host + "authors/" + user.username

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
            user.username = username

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
        user.delete()

        return JsonResponse({"success": "User deleted successfully."})
    
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
        displayName = request.POST.get('displayName')
        github = request.POST.get('github')
        profileImage = request.POST.get('profileImage')
        username = request.POST.get('username')
        password = request.POST.get('password')
        host = views.Host.host

        if (validate_password(password) == False):
            return JsonResponse({"error": "Password does not meet the requirements. Your password must contain at least 8 characters and at least 1 special character (!@#$%^&*)"}, status=400)

        user = User.objects.create(
            displayName = displayName,
            github = github,
            profileImage = profileImage,
            username = username,
            password = password,
            host = host
        )

        # Save the user
        user.save()

        page = user.host + "authors/" + user.username

        return JsonResponse({
            "type": "author",
            "id": user.id,
            "host": user.host,
            "displayName": user.displayName,
            "github": user.github,
            "profileImage": user.profileImage,
            "page": page
        }, safe=False, status=200)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def change_password(request, user_id):
    '''
    Changes the password of an user.

    Parameters:
        request: HttpRequest object containing the request with the new password.
        user_id: The id of the user to change the password.
    
    Returns:
        JsonResponse containing the success message if the password was updated successfully.
    '''
    if request.method == "PUT":
        user = get_object_or_404(User, pk=user_id)

        put = json.loads(request.body.decode('utf-8'))

        password = put.get('password')

        if (validate_password(password) == False):
            return JsonResponse({"error": "Password does not meet the requirements. Your password must contain at least 8 characters and at least 1 special character (!@#$%^&*)"}, status=400)

        user.password = password
        user.save()

        return JsonResponse({"success": "Password updated successfully."})
    
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


def validate_password(password):
    '''
    Validates the password based on the following rules:
    - At least 8 characters
    - At least 1 special character (!@#$%^&*)

    Parameters:
        password: The password to be validated.

    Returns:
        True if the password is valid, False otherwise.
    '''
    if len(password) < 8:
        return False
    
    special_characters = "!@#$%^&*"

    for character in password:
        if character in special_characters:
            return True
        
    return False