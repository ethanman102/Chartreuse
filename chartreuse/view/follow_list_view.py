from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User as AuthUser
from chartreuse.models import User,Follow
from django.views.generic.detail import DetailView
from urllib.parse import unquote, quote
from django.http import Http404 

class FollowListDetailView(DetailView):

    """
    Purpose: Serve associated files specified by the URL user url_id paramater to view either the users they are followed by or following
    """

    template_name = 'follow_list.html'
    context_object_name = 'user'
    model = User

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
        user = context['user']
        path = self.request.path
        if "following" in path:
            relationship = "following"
        else:
            relationship = "followers"
        context['relationship'] = relationship

        # On October 14, 2024 Asked ChatGPT: How to throw django 404 error
        if relationship != "following" and relationship != "followers":
            raise Http404("Page not found")
        elif relationship == "followers":
            follows = self.get_followers(user)
        else:
            follows = self.get_following(user)

        if len(follows) == 0:
            return context
        
        

        # need to be able to send the correct percent encoded url upon view-profile action, so percent encode all id's
        for follow_user in follows:
            follow_user.url_id = quote(follow_user.url_id,safe='')
        
        context['follows'] = follows
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

def view_profile_redirect(request,url_id):
    return redirect("chartreuse:profile",url_id=url_id)