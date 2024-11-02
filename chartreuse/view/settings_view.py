from django.views.generic.detail import DetailView
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
import json
from ..models import User, Post
from django.shortcuts import get_object_or_404
from urllib.parse import urlparse
import base64
from .support_functions import get_image_post
from urllib.request import urlopen

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action, api_view

@extend_schema(
    summary="Update the password for the current user",
    description=(
        "Allows an authenticated user to update their password by providing their current password and a new password."
        "\n\n**When to use:** Use this endpoint when a user wants to securely change their password."
        "\n\n**How to use:** Send a POST request containing `old_pass` (the current password) and `new_pass` (the new desired password) in JSON format."
        "\n\n**Why to use:** This API enhances security by allowing users to update their password, requiring the current password for verification."
        "\n\n**Why not to use:** Avoid using if you are content with your current password."
    ),
    request={
        "old_pass": str,
        "new_pass": str
    },
    responses={
        200: OpenApiResponse(
            description="Password successfully changed."
        ),
        400: OpenApiResponse(
            description="New password did not meet validation requirements."
        ),
        403: OpenApiResponse(
            description="Old password invalid."
        ),
        405: OpenApiResponse(
            description="Method not allowed"
        ),
    }
)    
@login_required
def update_password(request):
    """
    Updates the password for the currently authenticated user.

    Parameters:
        request: HttpRequest object containing the user's request data, including JSON with:
            - "old_pass": The user's current password (required for verification).
            - "new_pass": The new password the user wishes to set.

    Returns:
        JsonResponse:
            - 200: Success message when password is successfully changed.
            - 400: Error message if the new password does not meet validation requirements.
            - 403: Error message if the old password is incorrect.
            - 405: Error message if the request method is not allowed.
    """
    if request.method == "POST":

        data = json.loads(request.body)
        original_password = data.get("old_pass")
        new_password = data.get("new_pass")

        current_user = AuthUser.objects.get(username=request.user.username)
            
        
        if not current_user.check_password(original_password.strip()):
            response = JsonResponse({"error": "Old password invalid"}, status=403)
            return response
        
        # validate the password against our own validation steps for passwords.
        try:
            validate_password(new_password)
        except ValidationError as e:
            return JsonResponse({"error": e.messages}, status=400)
        
        current_user.set_password(new_password)

        # https://stackoverflow.com/questions/30466191/django-set-password-isnt-hashing-passwords
        # Required to save a User after set_password.
        # Stackoverflow Post: Django: set_password isn't hashing passwords?
        # Answered By: xyres on May 26, 2015
        current_user.save() 
        
        auth_login(request,current_user) # relogin the current user
        

        return JsonResponse({'success': 'Password successfully changed'},status=200)
    return HttpResponseNotAllowed(['POST'])
    

@extend_schema(
    summary="Update the display name for the current user",
    description=(
        "Allows an authenticated user to update their display name by providing a new display name in the request body."
        "\n\n**When to use:** Use this endpoint when a user wants to change their public display name."
        "\n\n**How to use:** Send a POST request with `display_name` as a JSON parameter containing the new desired display name."
        "\n\n**Why to use:** This endpoint provides a way for users to personalize or update their display name, which will be shown on their profile and in interactions across the application."
        "\n\n**Why not to use:** Avoid using if the display name update functionality is not required or if the request method is not allowed."
    ),
    request={
        "display_name": str
    },
    responses={
        200: OpenApiResponse(
            description="Display name successfully changed."
        ),
        404: OpenApiResponse(
            description="User not found."
        ),
        405: OpenApiResponse(
            description="Method not allowed: Only POST requests are supported."
        ),
    }
)
@login_required
def update_display_name(request):
    """
    Updates the display name for the currently authenticated user.

    Parameters:
        request: HttpRequest object containing the request data with JSON:
            - "display_name": The new display name the user wishes to set.

    Returns:
        JsonResponse:
            - 200: Success message when the display name is successfully changed.
            - 404: Error message if the user is not found.
            - 405: Error message if the request method is not POST.
    """
    if request.method == "POST":

        data = json.loads(request.body)
        new_display_name = data.get("display_name")

        current_auth_user = request.user
        current_user_model = get_object_or_404(User,user=current_auth_user)

        current_user_model.displayName = new_display_name
        current_user_model.save()

        return JsonResponse({'success': 'Display name successfully changed'},status=200)
    return HttpResponseNotAllowed(['POST'])
    
@extend_schema(
    summary="Remove the GitHub account associated with the current user",
    description=(
        "Allows an authenticated user to remove the GitHub account linked to their profile by confirming the current GitHub username. "
        "This endpoint accepts a DELETE request with the current GitHub username, unlinks it from the user's profile, and saves the changes."
        "\n\n**When to use:** Use this endpoint when a user wants to disassociate their GitHub account from their profile."
        "\n\n**How to use:** Send a DELETE request with `current_github` as a JSON parameter containing the currently associated GitHub username."
        "\n\n**Why to use:** This endpoint provides a way for users to remove their GitHub account association for privacy or profile updating purposes."
        "\n\n**Why not to use:** Avoid using if the GitHub account is not associated or if the request method is not DELETE."
    ),
    request={
        "current_github": str
    },
    responses={
        200: OpenApiResponse(
            description="Associated github removed"
        ),
        404: OpenApiResponse(
            description="User not found."
        ),
        405: OpenApiResponse(
            description="Method not allowed"
        ),
        500: OpenApiResponse(
            description="Server Side Implementation Error"
        ),
    }
)
@login_required
def remove_github(request):
    """
    Removes the GitHub account associated with the currently authenticated user.

    Parameters:
        request: HttpRequest object containing the request data with JSON:
            - "current_github": The GitHub username currently linked to the user's profile.

    Returns:
        JsonResponse:
            - 200: Success message if the GitHub association is successfully removed.
            - 404: Error message if the user is not found.
            - 405: Error message if the request method is not DELETE.
            - 500: Error message if the provided GitHub username does not match the user's associated GitHub.
    """
    if request.method == "DELETE":
        data = json.loads(request.body)

        current_github = data.get("current_github")
        current_auth_user = request.user
        current_user_model = get_object_or_404(User,user=current_auth_user)

        if (current_user_model.github != current_github):
            return JsonResponse({'error': 'Server Side Implementation Error'}, status=500)
        
        current_user_model.github = None
        current_user_model.save()
        
        return JsonResponse({'success': 'Associated github removed'},status=200)
    return HttpResponseNotAllowed(['DELETE'])
    
@extend_schema(
    summary="Add a GitHub account to the current user's profile",
    description=(
        "Allows an authenticated user to associate a GitHub account with their profile by providing a valid GitHub URL."
        "\n\n**When to use:** Use this endpoint when a user wants to link their GitHub account to their profile."
        "\n\n**How to use:** Send a PUT request with `github` as a JSON parameter containing the GitHub URL."
        "\n\n**Why to use:** This endpoint provides a way for users to add a GitHub account to their profile to showcase their projects and contributions."
        "\n\n**Why not to use:** Avoid using if the URL provided is not a GitHub link or if the request method is not PUT."
    ),
    request={
        "github": str
    },
    responses={
        200: OpenApiResponse(
            description="Github Added successfully"
        ),
        400: OpenApiResponse(
            description="Invalid GitHub URL"
        ),
        404: OpenApiResponse(
            description="User not found."
        ),
        405: OpenApiResponse(
            description="Method not allowed: Only PUT requests are supported."
        ),
    }
)
@login_required
def add_github(request):
    """
    Adds a GitHub account to the currently authenticated user's profile.

    Parameters:
        request: HttpRequest object containing the request data with JSON:
            - "github": The GitHub URL to be associated with the user's profile.

    Returns:
        JsonResponse:
            - 200: Success message if the GitHub account is added successfully.
            - 400: Error message if the provided GitHub URL is invalid.
            - 404: Error message if the user is not found.
            - 405: Error message if the request method is not PUT.
    """
    if request.method == "PUT":
        data = json.loads(request.body)

        github = data.get('github')

        # check to see if it is a github URL hostname..
        # https://stackoverflow.com/questions/9530950/parsing-hostname-and-port-from-string-or-url
        # Stack Overflow Post: Parsing hostname and port from string or url
        # Purpose: how to validate the hostname of a URL string
        # Answered by: Maksym Kozlenko on July 21, 2013
        host = urlparse(github).hostname

        if host == None or host.lower() != 'github.com':
            return JsonResponse({'error': 'Invalid Github URL'},status=400)
        
        current_auth_user = request.user
        current_user_model = get_object_or_404(User,user=current_auth_user)

        current_user_model.github = github
        current_user_model.save()

        return JsonResponse({'success': 'Github Added successfully'},status=200)
    return HttpResponseNotAllowed(['PUT'])

@extend_schema(
    summary="Upload a profile picture for the current user",
    description=(
        "Allows an authenticated user to upload a new profile picture, which will be saved as a base64-encoded image."
        "\n\n**When to use:** Use this endpoint to update the user's profile picture by sending a file in the request."
        "\n\n**How to use:** Send a POST request with the image file in the `request.FILES` payload."
        "\n\n**Why to use:** This endpoint updates the user's profile picture URL and provides an encoded version of the image."
        "\n\n**Why not to use:** Avoid using if you do not need a profile picture."
    ),
    request={
        "image": str
    },
    responses={
        200: OpenApiResponse(
            description="Profile picture updated",
            examples={"success": "Profile picture updated", "image": "base64-encoded-image-data"}
        ),
        400: OpenApiResponse(
            description="No file provided."
        ),
        404: OpenApiResponse(
            description="User not found."
        ),
        405: OpenApiResponse(
            description="Method not allowed."
        ),
    }
)
@login_required
def upload_profile_picture(request):
    """
    Uploads a profile picture for the currently authenticated user.

    Parameters:
        request: HttpRequest object containing the uploaded image file in `request.FILES`.

    Returns:
        JsonResponse:
            - 200: Success message if the profile picture is uploaded successfully.
            - 400: Error message if no file is provided in the request.
            - 404: Error message if the user is not found.
            - 405: Error message if the request method is not POST.
    """
    if request.method == "POST":

        file_to_read = None
        file_name_to_read = None
        # Resource: https://stackoverflow.com/questions/3111779/how-can-i-get-the-file-name-from-request-files
        # Stack overflow post: How can I get the file name from request.FILES?
        # Purpose: learned how to retrieve files of request.FILES wiithout knowing the file name,
        # Code inspired by mipadi's post on June 24, 2010
        for filename,file in request.FILES.items():
            file_name_to_read = filename
            file_to_read = file
            
        
        if (file_to_read == None or file_name_to_read == None):
            return JsonResponse({'error': 'No file provided'},status=400)
        
        mime_type = file_to_read.content_type + ';base64'
        
        image_data = file_to_read.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')

        current_auth_user = request.user
        current_user_model = User.objects.get(user = current_auth_user)

        new_picture = Post(
            title="profile pic",
            contentType = mime_type,
            content = encoded_image,
            user = current_user_model,
            visibility = 'DELETED'
        )
        new_picture.save()

        profile_pic_url = new_picture.url_id + '/image'

        current_user_model.profileImage = profile_pic_url
        current_user_model.save()
        return JsonResponse({'success':'Profile picture updated','image':encoded_image},status=200)

    return HttpResponseNotAllowed(['POST'])


@extend_schema(
    summary="Upload a profile picture from a URL for the current user",
    description=(
        "Allows an authenticated user to upload a new profile picture by providing an image URL."
        "\n\n**When to use:** Use this endpoint to update the user's profile picture with an image from a direct URL."
        "\n\n**How to use:** Send a POST request with a JSON body containing the `url` key with the image URL as the value."
        "\n\n**Why to use:** This endpoint retrieves, encodes, and stores the image, updating the user's profile image URL."
        "\n\n**Why not to use:** Avoid using if the image is not in .png, .jpg, or .jpeg format."
    ),
    request={
        "application/json": OpenApiResponse(
            description="JSON body containing an image URL.",
            examples={"url": "https://example.com/image.jpg"}
        )
    },
    responses={
        200: OpenApiResponse(
            description="Profile picture updated",
            examples={
                "success": "Profile picture updated",
                "image": "base64-encoded-image-data",
                "mimeType": "image/png;base64"
            }
        ),
        400: OpenApiResponse(description="Failed to retrieve image."),
        404: OpenApiResponse(description="User not found."),
        415: OpenApiResponse(description="Unsupported media type: only .png and .jpeg images are accepted."),
        405: OpenApiResponse(description="Method not allowed"),
    }
)
@login_required
def upload_url_picture(request):
    """
    Uploads a profile picture from a URL for the currently authenticated user.

    Parameters:
        request: HttpRequest object containing a JSON body with `url` key for the image URL.

    Returns:
        JsonResponse:
            - 200: Success message with base64-encoded image data and MIME type if the profile picture is uploaded successfully.
            - 400: Error message if the image could not be retrieved from the URL.
            - 404: Error message if the user is not found.
            - 415: Error message if the media type is unsupported (.png, .jpg, and .jpeg only).
            - 405: Error message if the request method is not POST.
    """
    if request.method == "POST":
        data = json.loads(request.body)

        image_url = data.get('url')

        # code for converting to URL borrowed with permission from Julia Dantas from our groups support_functions.py save_post file
        image_content = image_url.split('.')[-1]

        if image_content not in ['png','jpg','jpeg']:
            return JsonResponse({'error':'Invalid media type. (.png and .jpeg accepted)'},status=415)

        mime_type = 'image/' + image_content 
        try:
            with urlopen(image_url) as url:
                f = url.read()
                encoded_string = base64.b64encode(f).decode("utf-8")
        except Exception as e:
            return JsonResponse({'error':'Failed to retrieve image'},400)
        encoded_image = encoded_string

        current_auth_user = request.user
        current_user_model = User.objects.get(user=current_auth_user)

        new_picture = Post(
            title="profile pic",
            contentType = mime_type + ';base64',
            content = encoded_image,
            user = current_user_model,
            visibility = 'DELETED'
        )

        new_picture.save()

        profile_pic_url = new_picture.url_id + '/image'
        current_user_model.profileImage = profile_pic_url

        current_user_model.save()

        return JsonResponse({'success':'Profile picture updated','image':encoded_image,"mimeType":mime_type},status=200)
    return HttpResponseNotAllowed(['POST'])

            

class SettingsDetailView(DetailView):
    '''
    SettingsDetailView

    Purpose: display the settings Page, whilst creating a model object for the context dictionary based on the
    currently logged in User
    '''

    model = User
    template_name = "settings.html"
    context_object_name= "user"
        
    def get_object(self):
        # user's Id can't be obtained since the User model does not explicity state a primary key. Will retrieve the user by grabbing them by the URL pk param.
        authenticated_user = self.request.user
        user = get_object_or_404(User,user=authenticated_user)
        user.profileImage = get_image_post(user.profileImage)
        return user

