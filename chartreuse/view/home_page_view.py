from django.shortcuts import get_object_or_404
from chartreuse.models import User, Post, Follow
from django.views.generic.detail import DetailView
from urllib.parse import unquote, quote

class FeedDetailView(DetailView):
    '''
    Purpose: Serves posts that the user has access to

    Inherits From: DetailView 
    '''

    model = User  # Define the model for the user
    template_name = "home_page.html"
    context_object_name = "posts"

    def get_object(self):
        """
        Get the object from session data instead of the URL.
        Assumes the `url_id` is stored in the session.
        """
        url_id = self.request.session.get('url_id')  # Retrieve from session
        if url_id:
            return get_object_or_404(User, url_id=url_id)
        else:
            return None  # Or raise an exception if you want

    def get_queryset(self):
        '''
        Get the queryset based on the user's authentication status
        '''
        if self.request.user.is_authenticated:
            current_user = self.request.user
            current_user_model = get_object_or_404(User, user=current_user)

            # Get people that the user follows
            followers = get_followed(current_user_model.url_id)

            posts = []

            # Get the posts of the people that the user follows
            for follower in followers:
                user_id = follower['id']
                user_posts = get_public_posts(user_id)
                posts.extend(user_posts)
            
            
            # Get the user's own posts
            user_posts = get_public_posts(current_user_model.url_id)

            return user_posts
        else:
            # For anonymous users, show all public posts
            return get_public_posts()

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
        
        get_queryset = self.get_queryset()
        context['posts'] = get_queryset
        print(context)

        return context

def get_public_posts():
    '''
    Retrieves all public posts.

    Returns:
        JsonResponse with the list of public posts.
    '''
    # Get all public posts
    posts = Post.objects.filter(visibility='PUBLIC')

    return posts

def get_followed(author_id):
    '''
    Retrieves the list of users that the author follows.

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the author whose followed users are being retrieved.

    Returns:
        JsonResponse with the list of followers.
    '''
    decoded_author_id = unquote(author_id)

    # Fetch the author based on the provided author_id
    author = get_object_or_404(User, url_id=decoded_author_id)
    
    # Get all followers for the author
    followed = Follow.objects.filter(follower=author)

    followed_list = []

    # Create a list of follower details to be included in the response
    for follower in followed:
        user = follower.following
        follower_attributes = [
            {
                "type": "author",
                "id": f"{user.host}/authors/{user.user.id}",
                "host": user.host,
                "displayName": user.displayName,
                "page": f"{user.host}/authors/{user.user.id}",
                "github": user.github,
                "profileImage": user.profileImage
            }
        ]
        followed_list.append(follower_attributes)

    return followed_list

def get_public_posts(user_id):
    """
    Gets all public posts from a user.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        user_id: The id of the user who created the posts.
        post_id: The id of the post object.

    Returns:
        JsonResponse containing the post object.
    """
    decoded_user_id = unquote(user_id)
    author = User.objects.get(url_id=decoded_user_id)

    posts = Post.objects.filter(user=author, visibility='PUBLIC')

    return posts

def get_friends_posts(user_id):
    """
    Gets all friends posts from a user.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        user_id: The id of the user who created the posts.
        post_id: The id of the post objects.

    Returns:
        JsonResponse containing the post object.
    """
    decoded_user_id = unquote(user_id)
    author = User.objects.get(url_id=decoded_user_id)

    posts = Post.objects.filter(user=author, visibility='FRIENDS')

    return posts

def get_private_posts(user_id):
    """
    Gets all private posts from a user.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        user_id: The id of the user who created the posts.
        post_id: The id of the post objects.

    Returns:
        JsonResponse containing the post object.
    """
    decoded_user_id = unquote(user_id)
    author = User.objects.get(url_id=decoded_user_id)

    posts = Post.objects.filter(user=author, visibility='PRIVATE')

    return posts

def get_unlisted_posts(user_id):
    """
    Gets all unlisted posts from a user.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        user_id: The id of the user who created the posts.
        post_id: The id of the post object.

    Returns:
        JsonResponse containing the post objects.
    """
    decoded_user_id = unquote(user_id)
    author = User.objects.get(url_id=decoded_user_id)

    posts = Post.objects.filter(user=author, visibility='UNLISTED')

    return posts
