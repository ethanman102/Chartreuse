from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User as AuthUser
from chartreuse.models import User, Follow, Post, Like
from django.views.generic.detail import DetailView
from urllib.parse import unquote, quote
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied

class LikedListDetailView(DetailView):
    """
    Purpose: Serves a detail view of all auhtors that liked a post.

    Inherits From: DetailView
    """
    template_name = 'who_liked.html'
    context_object_name = 'user'
    model = User

    # Because get_context_data can not return anything other than a dict, must override get method to return a 401 since it does not have an exception form!
    # Used this Stack Overflow reference on how to properly override the get method of detail view: https://stackoverflow.com/questions/57645928/django-overriding-detail-view-get-method
    # Answer Author: Harold Holsappel on June 15, 2023.
    # Also used this reference for returning HTTP errors because get_context_data can only return a DICT: https://stackoverflow.com/questions/67263268/django-class-based-view-to-return-httpresponse-such-as-httpresponsebadrequest
    # Answered by: Abdul Aziz Barkat on April 26 2021
    # def get(self, request, *args, **kwargs):
    #     '''
    #     Purpose: Overriden DetailView method to be able to handle serving 401 unauthorized requests!
    #     '''
    #     path = self.request.path.lower().split("/")
    #     if "friends" in path and not self.request.user.is_authenticated:
    #         return HttpResponse("Unauthorized",status=401)
        

    #     return super().get(request, *args, **kwargs)

    def get_object(self):
        """
        Retrieve the post object based on the URL parameter 'post_id'.
        """
        url_id = self.kwargs.get('post_id')
        url_id = unquote(url_id)
        post = Post.objects.filter(url_id=url_id).first()
        return post

    def get_context_data(self, **kwargs):
        '''
        Constructs the context data for rendering the who liked detial view
        
        liked: List of User model objects of the Users that liked the post.
        '''
        context =  super().get_context_data(**kwargs)
        post = self.get_object()

        # Check authentication
        if self.request.user.is_authenticated:
            current_user = self.request.user
            current_user_model = get_object_or_404(User, user=current_user)

            # Ensure the request user has access to view the post details
            is_following = Follow.objects.filter(follower=current_user_model, followed=post.user).exists()
            is_followed = Follow.objects.filter(follower=post.user, followed=current_user_model).exists()
            post_owner = post.user
            if ((not is_followed) and (not is_following) and (post.visibility == "FRIENDS") and (post_owner != current_user_model)):
                return redirect('/chartreuse/homepage')

            # Get the list of likes on the post
            likes = Like.objects.filter(post=post)

            # Construct the list of authors that liked the post
            users_that_liked = []
            for like in likes:
                users_that_liked.append(
                    like.user
                )

            # Add the list of authors to the context
            context["liked"] = users_that_liked
       
        else:
            # Redirect if not authenticated
            return redirect('/chartreuse/homepage')
        
        return context
        


