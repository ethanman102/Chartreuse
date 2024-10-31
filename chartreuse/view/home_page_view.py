from django.shortcuts import get_object_or_404
from chartreuse.models import User, Follow, Like, FollowRequest, Post
from django.views.generic.detail import DetailView
from urllib.parse import quote
from chartreuse.view.support_functions import get_followed, get_all_public_posts, get_posts
from . import support_functions

class FeedDetailView(DetailView):
    '''
    Purpose: Serves posts that the user has access to

    Inherits From: DetailView 
    '''

    model = User
    template_name = "home_page.html"
    context_object_name = "posts"

    def get_object(self):
        """
        Get the object from session data instead of the URL.
        Assumes the `url_id` is stored in the session.
        """
        url_id = self.request.session.get('url_id')
        if url_id:
            return get_object_or_404(User, url_id=url_id)
        else:
            return None

    def get_posts(self):
        '''
        Get the queryset based on the user's authentication status
        '''
        if self.request.user.is_authenticated:
            current_user = self.request.user
            current_user_model = get_object_or_404(User, user=current_user)

            # Get people that the user follows
            following = get_followed(current_user_model.url_id)

            posts = []

            public_posts = get_all_public_posts().exclude(user=current_user_model)

            following_url_ids = [user.url_id for user in following]

            follow_requests = FollowRequest.objects.filter(requester=current_user_model)
            follow_request_url_ids = [follow_request.requestee.url_id for follow_request in follow_requests]

            # get all posts from the users that the current user follows
            for follower in following:
                unlisted_posts = get_posts(follower.url_id, 'UNLISTED')
                posts.extend(unlisted_posts)

                is_following = Follow.objects.filter(follower=current_user_model, followed=follower.url_id).exists()
                is_followed = Follow.objects.filter(follower=follower.url_id, followed=current_user_model).exists()

                if (is_following and is_followed):
                    friends_posts = get_posts(follower.url_id, 'FRIENDS')
                    posts.extend(friends_posts)

            for post in posts:
                post.following_status = 'Following'
            
            for post in public_posts:
                if (post.user.url_id in following_url_ids):
                    post.following_status = 'Following'
                elif (post.user.url_id in follow_request_url_ids):
                    post.following_status = 'Pending'
                else:
                    post.following_status = 'Follow'

            # Combine all posts and sort by date published
            posts.extend(public_posts)
            posts = sorted(posts, key=lambda post: post.published, reverse=True)

            for post in posts:
                post.likes_count = Like.objects.filter(post=post).count()
                post.url_id = quote(post.url_id, safe='')

                if post.contentType != ("text/plain" and "text/commonmark"):
                    post.content = f"data:{post.contentType};charset=utf-8;base64, {post.content}"
                
                post.user.profileImage = support_functions.get_image_post(post.user.profileImage)

            return posts
        
        else:
            posts = get_all_public_posts()

            for post in posts:
                post.likes_count = Like.objects.filter(post=post).count()
                post.url_id = quote(post.url_id, safe='')
                post.following_status = "Sign up to follow!"
                if post.contentType != "text/plain":
                    post.content = f"data:{post.contentType};charset=utf-8;base64, {post.content}"
            
            return posts

    def get_user_details(self):
        '''
        Get the user details for the current user
        '''
        if self.request.user.is_authenticated:
            current_user = self.request.user
            current_user_model = get_object_or_404(User, user=current_user)

            current_user_model.url_id = quote(current_user_model.url_id, safe='')

            return current_user_model
        else:
            return None

    def get_context_data(self, **kwargs):
        '''
        Context Dictionary Structure:
        {
            posts: (the Post model object)
            logged_in: (Depicts if user is authenticated and has full page access)
        }
        '''
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['logged_in'] = True
        else:
            context['logged_in'] = False
        
        posts = self.get_posts()
        context['posts'] = posts

        user_details = self.get_user_details()
        context['user_details'] = user_details

        return context