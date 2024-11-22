from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from chartreuse.models import User, Settings
from chartreuse.views import Host
from django.views.decorators.csrf import csrf_exempt

def signup(request):
    return render(request, 'signup.html')

@csrf_exempt
def save_signup(request):
    if request.method == 'POST':
        # Get data from the form
        username = request.POST.get('username')
        password_1 = request.POST.get('password1')
        password_2 = request.POST.get('password2')
        displayName = request.POST.get('displayname')
        github = request.POST.get('github', '')  # Default to empty string if not provided
        profileImage = request.POST.get('profile_image', '')  # Default to empty string if not provided

        # Check if the username already exists
        if AuthUser.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists."}, status=400)

        # Check if passwords match
        if password_1 != password_2:
            return JsonResponse({"error": "Passwords do not match."}, status=400)

        # Validate password
        try:
            validate_password(password_1)
        except ValidationError as e:
            return JsonResponse({"error": e.messages}, status=400)

        # Create the AuthUser instance
        authUser = AuthUser.objects.create_user(username=username)
        authUser.set_password(password_1)
        singleton_settings = Settings.get_instance()
        if singleton_settings.approval_required:    # set active status of newly created account as False is approval is required
            authUser.is_active = False
        authUser.save()

        # Get the host from the request
        current_host = Host(request.get_host())

        if (profileImage == ""):
            profileImage = f'https://{current_host.host}/static/images/default_pfp_1.png'

        # Create the custom User model instance
        id = f'https://{current_host.host}/chartreuse/api/authors/{authUser.id}'
        # id = "https://" + current_host.host + "/authors/" + str(authUser.id)
        user = User.objects.create(
            url_id=id,
            displayName=displayName,
            github=github,
            profileImage=profileImage,
            host="https://" + current_host.host + '/chartreuse/api/',
            user=authUser
        )

        # Save the custom User model
        user.save()

        # Redirect to the login page after successful signup
        return redirect('/chartreuse/login')
