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


    def get(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        post_id = unquote(post_id)
        post = get_object_or_404(Post,url_id=post_id)
        


        if not self.request.user.is_authenticated:
            return redirect('/chartreuse/homepage')
        
        current_auth_user = self.request.user
        current_user_model = get_object_or_404(User,user=current_auth_user)
        
        is_following = Follow.objects.filter(follower=current_user_model, followed=post.user).exists()
        is_followed = Follow.objects.filter(follower=post.user, followed=current_auth_user).exists()
        
        if ((not is_followed) and (not is_following) and (post.visibility == "FRIENDS") and (post.user != current_user_model)):
            return redirect('/chartreuse/homepage')

        return super().get(request, *args, **kwargs)

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
        
        return context
        


