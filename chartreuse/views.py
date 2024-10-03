from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from .models import User
from django.views.generic.detail import DetailView

class Host():
    host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/api/"

def signup(request):
    return render(request, 'signup.html')

def save_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password_1 = request.POST.get('password1')
        password_2 = request.POST.get('password2')
        displayname = request.POST.get('displayname')
        github = request.POST.get('github')

        # create the auth user first, bacause User has a one to one relationship with it
        auth_user = AuthUser(username=username, password=password_1)
        auth_user.save()

        # now create the User
        user = User(user=auth_user, displayName=displayname, github=github)
        user.save()

        return redirect('chartreuse/login')

def login(request):
    return render(request, 'login.html')


class ProfileDetailView(DetailView):
    model = User
    template_name = "chartreuse/profile.html"
    context_object_name= "profile"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user = context['profile']
        
        return context
        

    def get_object(self):
        user = super().get_object()
        return user

        