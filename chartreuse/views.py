from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from .models import User,Like,Comment,Post
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

    '''
    Purpose: Serve associated files related to the user specified in the URL pk

    Inherits From: DetailView (Allows us to obtain all fields associated to a user whilst adding more
    By overriding get_context_data, and retreiving the nested user primary key in the url by overriding get_object)

    '''


    model = User
    template_name = "chartreuse/profile.html"
    context_object_name= "profile"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user = context['profile']
        # Overriden to get these addition counts.
        context['like_count'] = Like.objects.filter(user=user).count()
        context['comment_count'] = Comment.objects.filter(user=user).count()
        context['post_count'] = Post.objects.filter(user=user).count()
        return context
        

    def get_object(self):
        # user's Id can't be obtained since the User model does not explicity state a primary key. Will retrieve the user by grabbing them by the URL pk param.
        user = super().get_object()
        return user

        