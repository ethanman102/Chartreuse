from django.shortcuts import render
from django.contrib.auth import logout as auth_logout

def landing_page(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return render(request, 'landing_page.html')