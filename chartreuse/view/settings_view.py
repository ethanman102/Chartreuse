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
from .post_utils import get_image_post
from urllib.request import urlopen

@login_required
def update_password(request):
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
    

@login_required
def update_display_name(request):
    if request.method == "POST":

        data = json.loads(request.body)
        new_display_name = data.get("display_name")

        current_auth_user = request.user
        current_user_model = get_object_or_404(User,user=current_auth_user)

        current_user_model.displayName = new_display_name
        current_user_model.save()

        return JsonResponse({'success': 'Display name successfully changed'},status=200)
    return HttpResponseNotAllowed(['POST'])
    
@login_required
def remove_github(request):
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
    
@login_required
def add_github(request):
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


@login_required
def upload_profile_picture(request):
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


@login_required
def upload_url_picture(request):
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

