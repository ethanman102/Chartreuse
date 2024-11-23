from django.shortcuts import get_object_or_404
from chartreuse.models import User, Follow, Like, FollowRequest, Node
from django.views.generic.detail import DetailView
from urllib.parse import quote
from chartreuse.view.post_utils import get_all_public_posts, get_posts, get_image_post,prepare_posts
from chartreuse.view.follow_utils import get_followed
from django.core.paginator import Paginator
import requests


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

            reposts = public_posts.filter(contentType='repost')
            needed_reposts = reposts.filter(user__url_id__in=following_url_ids)
            unneeded_reposts = reposts.difference(needed_reposts)

            public_posts = public_posts.difference(unneeded_reposts)

            confirmed_follows = set()
            unconfirmed_follows = set()
            # get all posts from the users that the current user follows
            for follower in following:
                node_queryset = Node.objects.filter(host=follower.host,follow_status="OUTGOING",status="ENABLED")

                if not node_queryset.exists():
                    continue # skip showing posts from a non existant node connection!

                if (follower.host != current_user_model.host) and (follower.url_id not in confirmed_follows or follower.url_id not in unconfirmed_follows):
                    node_queryset = Node.objects.filter(host=follower.host,follow_status="OUTGOING",status="ENABLED")
                    if not node_queryset.exists():
                        unconfirmed_follows.add(follower.url_id)
                        continue # skip showing posts from a non existant node connection!

                    # make a request to see if they are following remotely.
                    node = node_queryset[0]
                    auth = (node.username,node.password)
                    url = f"{follower.url_id}/followers/{quote(current_user_model.url_id,safe='')}"

                    try:
                        response = requests.get(url,auth=auth)
                        if response.status_code == 404:
                            unconfirmed_follows.add(follower.url_id)
                            continue
                        else:
                            confirmed_follows.add(follower.url_id)
                    except:
                        unconfirmed_follows.add(follower.url_id)

                elif follower.url_id in unconfirmed_follows:
                    continue

                unlisted_posts = get_posts(follower.url_id, 'UNLISTED')
                posts.extend(unlisted_posts)

                is_following = Follow.objects.filter(follower=current_user_model, followed=follower.url_id).exists()
                is_followed = Follow.objects.filter(follower=follower.url_id, followed=current_user_model).exists()

                if (is_following and is_followed):
                    friends_posts = get_posts(follower.url_id, 'FRIENDS')
                    posts.extend(friends_posts)

            for post in posts:
                post.following_status = 'Following'

            # Combine all posts and sort by date published
            posts.extend(public_posts)
            posts = sorted(posts, key=lambda post: post.published, reverse=True)

            posts = prepare_posts(posts)

            for post in posts:
                if (post.user.url_id in following_url_ids):
                    post.following_status = 'Following'
                elif (post.user.url_id in follow_request_url_ids):
                    post.following_status = 'Pending'
                else:
                    post.following_status = 'Follow'
                
                
                post.user.profileImage = get_image_post(post.user.profileImage)

            return posts
        
        else:
            posts = get_all_public_posts()

            for post in posts:
                post.likes_count = Like.objects.filter(post=post).count()
                post.url_id = quote(post.url_id, safe='')
                post.following_status = "Sign up to follow!"
                if (post.contentType != "text/plain") and (post.contentType != "text/markdown"):
                    post.content = f"data:{post.contentType};charset=utf-8;base64, {post.content}"
                post.user.profileImage = get_image_post(post.user.profileImage)
            
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
        paginator = Paginator(posts, 5)  # Show 5 posts per page
        page_number = self.request.GET.get('page')  # Get the current page number from the URL
        page_obj = paginator.get_page(page_number)  # Get the posts for the current page
        context['posts'] = page_obj 

        user_details = self.get_user_details()
        context['user_details'] = user_details

        return context