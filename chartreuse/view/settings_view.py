from django.views.generic.detail import DetailView
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
import json
from ..models import User
from django.shortcuts import get_object_or_404

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
            

class SettingsDetailView(DetailView):
    '''
    SettingsDetailView

    Purpose: display the settings Page, whilst creating a model object for the context dictionary based on the
    currently logged in User
    '''

    model = AuthUser
    template_name = "settings.html"
    context_object_name= "user"
        
    def get_object(self):
        # user's Id can't be obtained since the User model does not explicity state a primary key. Will retrieve the user by grabbing them by the URL pk param.
        authenticated_user = self.request.user
        return authenticated_user

