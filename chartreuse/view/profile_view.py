from django.shortcuts import redirect, get_object_or_404
from chartreuse.models import User,Like,Comment,Post,Follow,FollowRequest, Node
from django.views.generic.detail import DetailView
from django.http import HttpResponseNotAllowed
from urllib.parse import unquote, quote
from . import post_utils
from ..views import Host
import requests
import base64

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
        remote_check = request.POST.get('remote-follow')
        requester_user = get_object_or_404(User,url_id=requester)
        requestee_user = get_object_or_404(User,url_id=requestee)
        if remote_check != None:
            # Can assume that the user is already following the remote author now..

            remote_node = Node.objects.filter(follow_status='OUTGOING',host=requestee_user.host)
            if remote_node.count() != 1:
                return redirect("chartreuse:profile",url_id=quote(requestee,safe=''))
            
            remote_node = remote_node[0]
            username = base64.b64encode(bytes(remote_node.username,encoding='utf-8')).decode('utf-8')
            password = base64.b64encode(bytes(remote_node.password,encoding='utf-8')).decode('utf-8')


            follow = Follow(follower=requester_user,followed=requestee_user) # create the new follow!
            follow.save()

            data = {
                'type': 'follow',
                'summary':'actor wants to follow object',
                'actor':
                {
                    'type':'author',
                    'id': requester_user.url_id,
                    'host': requester_user.host,
                    'displayName': requester_user.displayName,
                    'page': f'{requester_user.host}/authors/{requester_user.url_id}/',
                    'github':requester_user.github,
                    'profileImage': requester_user.github
                },
                'object':{
                    'type':'author',
                    'id': requestee_user.url_id,
                    'host': requestee_user.host,
                    'displayName': requester_user.displayName,
                    'page': f'{requestee_user.host}/authors/{requestee_user.url_id}/',
                    'github':requestee_user.github,
                    'profileImage': requestee_user.github
                }
            }

            url = f'{requestee_user.host}authors/{quote(requestee_user.url_id,safe='')}/inbox/'
            print('URL MANN',url)

            headers = {
                'Authorization' : f'Basic {username}:{password}',
                'Content-Type': 'application/json; charset=utf-8'
            }
            response = requests.post(url, headers=headers, json=data)
            print('WE REACH HERE?')
            print(response.status_code,'WOAH')
            
        else:
            FollowRequest.objects.create(requestee=requestee_user,requester=requester_user)
        return redirect("chartreuse:profile",url_id=quote(requestee,safe=''))
    return HttpResponseNotAllowed(["POST"])




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
        is_following: (If the user is foreign this key will be here, depicts if they are following the page owner or not.)
        sent_request: (Bool if the user is NOT already following, but did they sent a follow request?)
        follow_relationship: "Friends/Following" depicts whether the following is mutual or unmutual!
        posts: Contains all the posts by the author who owns the profile page that the current user visiting can see.
        }
        
        '''
        context = super().get_context_data(**kwargs)
        user = context['profile']
        context['owner_id'] = quote(user.url_id,safe='')
        
        hostname = self.request.get_host()
        host_obj = Host(hostname)



        if ('https://' + host_obj.host + '/chartreuse/api/') != user.host:
            context['remote'] = 'REMOTE author'
        

        context['profile'].profileImage = post_utils.get_image_post(context['profile'].profileImage)

        post_access = "public" # default following status, will be updated after!

        # checking if user is authenticated or anonymous
        if self.request.user.is_authenticated:
            context['logged_in'] = True
            # if logged in, check if user owns the current page or that's being visited or not...
            current_user = self.request.user
            print(current_user)
            current_user_model = get_object_or_404(User, user=current_user)  
            print(current_user_model)
            if user.url_id == current_user_model.url_id:
                # owns the page, should not display follow button etc...
                context['viewer_id'] = quote(current_user_model.url_id,safe='')
                context['owner'] = True
                context['requests'] = self.prepare_follow_requests(user)
                post_access = "all"
            else:
                context['viewer_id'] = quote(current_user_model.url_id,safe='')
                # check if the user if following or not...
                follow = Follow.objects.filter(follower=current_user_model,followed=user)
                if follow.count() == 0:
                    context['is_following'] = False
                    post_access = "public"
                    # check if a follow request has been sent or not!
                    follow_request  = FollowRequest.objects.filter(requestee=user,requester=current_user_model)
                    if follow_request.count() > 0:
                        context['sent_request'] = True
                    else:
                        context['sent_request'] = False
                else:
                    context['is_following'] = True
                    post_access = "unlisted"
                    # check if the user is following them back or not! (friends)
                    if Follow.objects.filter(followed=current_user_model,follower=user).exists():
                        context['follow_relationship'] = "Friends"
                        post_access = "all"
                    else:
                        context['follow_relationship'] = "Following"
        else:
            context['logged_in'] = False
        
        # Statistics
        context['like_count'] = Like.objects.filter(user=user).count()
        context['comment_count'] = Comment.objects.filter(user=user).count()
        context['post_count'] = Post.objects.filter(user=user).count()

        # Relationship Counts
        context['followers'] = Follow.objects.filter(followed=user).count()
        context['following'] = Follow.objects.filter(follower=user).count()

        # posts that can be viewed by the current user visiting.
        posts = self.get_posts(post_access,user)
        posts = post_utils.prepare_posts(posts)
        context['posts'] = posts
        

        return context
        

    def get_object(self):
        # user's Id can't be obtained since the User model does not explicity state a primary key. Will retrieve the user by grabbing them by the URL pk param.
       
        user_id = unquote(self.kwargs['url_id'])
        user = get_object_or_404(User,url_id=user_id)

        return user
    
    def prepare_follow_requests(self,user):
        '''
        Purpose: Runs if the User is logged in and grabs all follow requests for a specific user. Url_id's are percent encoded to be sent to profile page.

        # Arguments:
        user: The user object for the current profile page!
        '''
        follow_requests = FollowRequest.objects.filter(requestee=user)
        requests = [fk for fk in follow_requests]
        for follow_request in requests:
            if (follow_request.requester.url_id != user.url_id):
                follow_request.requester.url_id = quote(follow_request.requester.url_id,safe='')
                follow_request.requestee.url_id = quote(follow_request.requestee.url_id,safe='')
        return follow_requests
    
   

    def get_posts(self,post_access,user):

        '''
        Purpose: Get all visible posts that should appear on a user's profile page.

        Arguments: 
        user: The current user who owns the current page being viewed!
        post_access: the type of posts the user should be able to see!
        '''


        # This stackoverflow post allowed us to check how to do an OR query in Django: https://stackoverflow.com/questions/6567831/how-to-perform-or-condition-in-django-queryset
        # Relevant Response Post Date was: Author: hobs Date: October 11 2012
        if post_access == "public":
            posts = Post.objects.filter(visibility="PUBLIC",user=user)
        elif post_access == "unlisted":
            posts = Post.objects.filter(visibility="PUBLIC",user=user) | Post.objects.filter(visibility="UNLISTED",user=user)
        else:
            posts = Post.objects.filter(user=user).exclude(visibility="DELETED")

        # Resource: https://www.w3schools.com/django/django_queryset_orderby.php 
        # This Resource by W3 Schools titled: 'Django QuerySet - Order By' helped us to understand how to order a queryset from descending order!
        posts.order_by("-published")
        posts = [post for post in posts]
        posts = sorted(posts, key=lambda post: post.published, reverse=True)
        
        for post in posts:
            post.user.profileImage = post_utils.get_image_post(post.user.profileImage)

        return posts
        

