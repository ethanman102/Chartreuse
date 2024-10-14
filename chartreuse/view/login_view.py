from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

def login(request):
    return render(request, 'login.html')

@csrf_exempt
def save_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({"error": "Username and password are required."}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
        
        return redirect('/chartreuse/homepage')