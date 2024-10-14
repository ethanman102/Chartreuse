from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from .models import User,Like,Comment,Post,Follow,FollowRequest
from django.views.generic.detail import DetailView
from django.http import HttpResponseNotAllowed
from urllib.parse import unquote, quote


class Host():
    host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

def follow_accept(request,followed,follower):

    '''
    Purpose: View to interact with the follow requests database by deleting a request and processing the request into a new follower

    Arguments:
    request: Request body containing the followed id and the follower id to process into the database.
    followed: the primary key of the User object getting followed.
    follower: the primary key of the User object doing the following
    '''
    
    if request.method == "POST": # get the request body.
        followed = unquote(followed)
        follower = unquote(follower)
        followed_user = get_object_or_404(User,url_id=followed)
        following_user = get_object_or_404(User,url_id=follower)
        follow_request = get_object_or_404(FollowRequest,requester=following_user,requestee=followed_user)
        follow = Follow(follower=following_user,followed=followed_user) # create the new follow!
        follow.save()
        follow_request.delete()
        return redirect('chartreuse:profile',url_id=quote(followed,safe=''))
    
    return HttpResponseNotAllowed(["POST"])

def follow_reject(request,followed,follower):
    '''
    Purpose: View to interact with the follow requests database by rejecting a follow request and not processing it into a follow!!

    Arguments:
    request: Request body containing the id's of who is to be followed and who is following
    followed: the primary key of the User object getting followed.
    follower: the primary key of the User object doing the following
    '''
    if request.method == "POST":
        followed = unquote(followed)
        follower = unquote(follower)
        followed_user = get_object_or_404(User,url_id=followed)
        following_user = get_object_or_404(User,url_id=follower)
        follow_request = get_object_or_404(FollowRequest,requester=following_user,requestee=followed_user)
        follow_request.delete()
        return redirect("chartreuse:profile",url_id=quote(followed,safe=''))
    return HttpResponseNotAllowed(["POST"])


def profile_unfollow(request,followed,follower):
    '''
    Purpose: View to interact with the user to unfollow the person on the current page through a form submission.

    Arguments:
    request: Request with body containing the id's of who is going to be unfollowed and who is currently trying to unfollow
    followed: the id of the user who is currently followed but is about to be unfollowed
    follower: the primary key of the user who is currently following but about to be removed from the follow.
    '''

    if request.method == "POST":
        followed = unquote(followed)
        follower = unquote(follower)
        followed_user = get_object_or_404(User,url_id=followed)
        following_user = get_object_or_404(User,url_id=follower)
        follow = get_object_or_404(Follow,followed=followed_user,follower=following_user)
        follow.delete()
        return redirect("chartreuse:profile",url_id=quote(followed,safe=''))
    return HttpResponseNotAllowed(["POST"])

def profile_follow_request(request,requestee,requester):
    '''
    Purpose: View to interact with the user to send a follow request to the current user profile on the UI page

    Arguments:
    request: Request with body containing the ID's of whos in the follow request relationship
    requestee: the id of the user who is being asked to get followed
    requester: the id of the user who is sending the follow request
    '''

    if request.method == "POST":
        requestee = unquote(requestee)
        requester = unquote(requester)
        requester_user = get_object_or_404(User,url_id=requester)
        requestee_user = get_object_or_404(User,url_id=requestee)
        FollowRequest.objects.create(requestee=requestee_user,requester=requester_user)
        return redirect("chartreuse:profile",url_id=quote(requestee,safe=''))
    return HttpResponseNotAllowed(["POST"])


def error(request):
    '''
    Purpose: View to render a generic error page


    Arguments:
    request: Request object
    '''
    return render(request, 'error.html')

class ProfileDetailView(DetailView):

    '''
    Purpose: Serve associated files related to the user specified in the URL pk

    Inherits From: DetailView (Allows us to obtain all fields associated to a user whilst adding more
    By overriding get_context_data, and retreiving the nested user primary key in the url by overriding get_object)

    '''


    model = User
    template_name = "profile.html"
    context_object_name= "profile"

    def get_context_data(self,**kwargs):


        '''
        Context Dictionary Structure:
        {
        profile: (the User model object - NOT AUTHUSER - )
        viewer_id: (the id if the user viewing the page. this is percent encoded...) 
        owner_id: (the percent encoded id of the user who owns the page!)
        logged_in: (Depicts if user is authenticated and has full page access)
        owner: (If the logged in user is viewing their own page)
        requests: (A list of follow request objects)
        following: (If the user is foreign this key will be here, depicts if they are following the page owner or not.)
        sent_request: (Bool if the user is NOT already following, but did they sent a follow request?)
        }
        
        '''

        context = super().get_context_data(**kwargs)
        user = context['profile']

        # checking if user is authenticated or anonymous
        if self.request.user.is_authenticated:
            context['logged_in'] = True
            # if logged in, check if user owns the current page or that's being visited or not...
            current_user = self.request.user
            current_user_model = get_object_or_404(User,user=current_user)
            page_user = get_object_or_404(User,url_id=unquote(self.kwargs['url_id']))
            if page_user.url_id == current_user_model.url_id:
                # owns the page, should not display follow button etc...
                context['owner'] = True
                follow_requests = FollowRequest.objects.filter(requestee=page_user)
                requests = [fk for fk in follow_requests]
                for follow_request in requests:
                    follow_request.follower.url_id = quote(follow_request.follower.url_id,safe='')
                    follow_request.followed.url_id = quote(follow_request.followed.url_id,safe='')
                context['requests'] = requests
            else:

                context['viewer_id'] = quote(current_user_model.url_id,safe='')
                context['owner_id'] = quote(page_user.url_id,safe='')
                # check if the user if following or not...
                follow = Follow.objects.filter(follower=current_user,followed=page_user)
                if follow.count() == 0:
                    # check if a follow request has been sent or not!
                    follow_request  = FollowRequest.objects.filter(requestee=page_user,requester=current_user)
                    if follow_request.count() != 0:
                        context['sent_request'] = True
                else:
                    context['following'] = True

        # Overriden to get these addition counts.
        context['like_count'] = Like.objects.filter(user=user).count()
        context['comment_count'] = Comment.objects.filter(user=user).count()
        context['post_count'] = Post.objects.filter(user=user).count()
        context['followers'] = Follow.objects.filter(followed=user).count()
        context['following'] = Follow.objects.filter(follower=user).count()
        
    
        return context
        

    def get_object(self):
        # user's Id can't be obtained since the User model does not explicity state a primary key. Will retrieve the user by grabbing them by the URL pk param.
       
        user_id = unquote(self.kwargs['url_id'])
        return get_object_or_404(User,url_id=user_id)
        

