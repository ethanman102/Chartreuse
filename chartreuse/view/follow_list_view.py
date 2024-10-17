from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User as AuthUser
from chartreuse.models import User,Follow
from django.views.generic.detail import DetailView
from urllib.parse import unquote, quote
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied

class FollowListDetailView(DetailView):

    """
    Purpose: Serve associated files specified by the URL user url_id paramater to view either the users they are followed by or following
    """

    template_name = 'follow_list.html'
    context_object_name = 'user'
    model = User

    # Because get_context_data can not return anything other than a dict, must override get method to return a 401 since it does not have an exception form!
    # Used this Stack Overflow reference on how to properly override the get method of detail view: https://stackoverflow.com/questions/57645928/django-overriding-detail-view-get-method
    # Answer Author: Harold Holsappel on June 15, 2023.
    # Also used this reference for returning HTTP errors because get_context_data can only return a DICT: https://stackoverflow.com/questions/67263268/django-class-based-view-to-return-httpresponse-such-as-httpresponsebadrequest
    # Answered by: Abdul Aziz Barkat on April 26 2021
    def get(self, request, *args, **kwargs):
        '''
        Purpose: Overriden DetailView method to be able to handle serving 401 unauthorized requests!
        '''
        path = self.request.path.lower().split("/")
        if "friends" in path and not self.request.user.is_authenticated:
            return HttpResponse("Unauthorized",status=401)
        

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        '''
        Context Dictionary Structure:
        {
            user: The User model for the User we are viewing their followers / followings
            relationship: param from the URL to adjust if we are viewing followers or followings of the user
            follows: User model objects of the followings or follower User. PSA: url_id are percent encoded before being sent
        }
        
        '''
        context =  super().get_context_data(**kwargs)
        # https://stackoverflow.com/questions/10533302/how-to-get-the-url-path-of-a-view-function-in-django
        # How to get the url path of a view function in django
        # Answered by Ashley H. November 18, 2020
        page_user = context['user']
        path = self.request.path.lower().split("/")
        if "following" in path:
            relationship = "following"
        elif "followers" in path:
            relationship = "followers"
        elif "friends" in path:
            # required to be the owner of the friends list and authenticated in order to view the friends list!!!
            current_user = User.objects.get(user=self.request.user)
            if current_user.url_id != page_user.url_id:
                raise PermissionDenied
            relationship = "friends"
        
        context['relationship'] = relationship

        # On October 14, 2024 Asked ChatGPT: How to throw django 404 error
        # Grab appropiate group of following relationships
        if relationship != "following" and relationship != "followers" and relationship != "friends":
            raise Http404("Page not found")
        elif relationship == "followers":
            follows = self.get_followers(page_user)
        elif relationship == "following":
            follows = self.get_following(page_user)
        else:
            follows = self.get_friends(page_user)

        if len(follows) == 0:
            return context
        
        # need to be able to send the correct percent encoded url upon view-profile action, so percent encode all id's
        for follow_user in follows:
            follow_user.url_id = quote(follow_user.url_id,safe='')
        
        context['follows'] = follows
        # Must quote url_id of the owner of the list to ensure back button works correctly to redirect to the profile.
        page_user.url_id = quote(page_user.url_id,safe='')
        return context
            
    def get_object(self):
        user_id = unquote(self.kwargs['user_id'])
        return get_object_or_404(User,url_id=user_id)
    
    def get_following(self,user):
        '''
        Purpose: Portion of the View that returns a queryset of all following for that user.

        Arguments:
        user: The User Model object to find the the users being followed by this user

        '''
        follows = Follow.objects.filter(follower = user)
        return [follow.followed for follow in follows]
        

    def get_followers(self,user):
        '''
        Purpose: Portion of the View that returns a queryset of all followers for the user.

        Arguments:
        user: The User Model object to find the followers for
        '''
        follows = Follow.objects.filter(followed = user)
        return [follow.follower for follow in follows]
    
    def get_friends(self,user):
        '''
        Purpose: Portion of the View that returns a queryset of all followers for the user.

        Arguments:
        user: The User Model object to find the followers for
        '''
        user_follows = Follow.objects.filter(follower=user)
        user_followed_by = Follow.objects.filter(followed=user)
        print(user_follows)

        friends = list()
        for author in user_follows:
            author = author.followed
            for author2 in user_followed_by:
                author2 = author2.follower
                if author.url_id== author2.url_id:
                    friends.append(author)
                    break
        
        return friends
        


