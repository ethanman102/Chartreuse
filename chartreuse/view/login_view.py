from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User as AuthUser

def login(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return render(request, 'login.html')

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('/chartreuse/')

@csrf_exempt
def save_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({"error": "Username and password are required."}, status=400)

        # find the user object first
        user = AuthUser.objects.filter(username=username).first()

        if user is not None:
            if user.is_active:
                # log user in, if active
                active_user = authenticate(request, username=username, password=password)
                if active_user != None:
                    auth_login(request, active_user)
                else: 
                    return JsonResponse({"error": "Invalid password."}, status=401)
            else:
                return JsonResponse({"error": "Account is not active."}, status=401)
        else:
            return JsonResponse({"error": "The username does not exist."}, status=401)
        
        return redirect('/chartreuse/homepage')