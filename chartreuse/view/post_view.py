from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from chartreuse.models import Post, Like, Follow, User, FollowRequest
from urllib.parse import quote
from django.shortcuts import redirect

class PostDetailView(DetailView):
    '''
    Purpose: Serves a detailed view of a single post that the user has access to.

    Inherits From: DetailView 
    '''
    model = Post
    template_name = "view_post.html"
    context_object_name = "post"

    def get_object(self):
        """
        Retrieve the post object based on the URL parameter 'url_id'.
        """
        url_id = self.kwargs.get('post_id')
        print(self.kwargs.get('post_id'))
        print(self.kwargs.get("url_id"))
        post = get_object_or_404(Post, url_id=url_id)
        return post

    def get_context_data(self, **kwargs):
        '''
        Builds the context data for rendering the post detail page.
        '''
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        post.likes_count = Like.objects.filter(post=post).count()

        current_user_model = None

        if self.request.user.is_authenticated:
            current_user = self.request.user
            current_user_model = get_object_or_404(User, user=current_user)

            is_following = Follow.objects.filter(follower=current_user_model, followed=post.user.url_id).exists()
            requested_follow = FollowRequest.objects.filter(requester=current_user_model, requestee=post.user).exists()
            if (is_following):
                post.following_status = "Following"
            elif (requested_follow):
                post.following_status = "Pending"
            else:
                post.following_status = "Follow"

            is_followed = Follow.objects.filter(follower=post.user, followed=current_user_model).exists()
            if ((not is_followed) and (not is_following) and (post.visibility == "FRIENDS")):
                return redirect('/chartreuse/homepage')
            
        else:
            post.following_status = "Follow"

        post.url_id = quote(post.url_id, safe='')

        if post.contentType != "text/plain":
            post.content = f"data:{post.contentType};charset=utf-8;base64, {post.content}"

        context['post'] = post
        context['logged_in'] = self.request.user.is_authenticated
        if (post.user == current_user_model):
            context['is_author'] = True
        context['user_details'] = current_user_model

        return context