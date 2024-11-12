from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from chartreuse.models import User
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
        profileImage = request.POST.get('profile_image', 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/static/images/default_pfp_1.png')  # Default to empty string if not provided

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
        authUser.is_active = False
        authUser.save()

        if (profileImage == ""):
            profileImage = 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/static/images/default_pfp_1.png'

        # Get the host from the request
        Host(request.get_host)

        # Create the custom User model instance
        id = Host.host + "authors/" + str(authUser.id)
        user = User.objects.create(
            url_id=id,
            displayName=displayName,
            github=github,
            profileImage=profileImage,
            host=Host.host,
            user=authUser
        )

        # Save the custom User model
        user.save()

        # Redirect to the login page after successful signup
        return redirect('/chartreuse/login')
