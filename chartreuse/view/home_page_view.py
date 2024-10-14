from django.shortcuts import get_object_or_404
from chartreuse.models import User, Post, Follow, Like
from django.views.generic.detail import DetailView
from urllib.parse import unquote, quote
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json

import base64
from urllib.request import urlopen
from django.http import JsonResponse
from urllib.parse import unquote
from django.views.decorators.csrf import csrf_exempt

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

            if len(following) == 0:
                posts = get_all_public_posts()
                for post in posts:
                    post.likes_count = Like.objects.filter(post=post).count()
                    post.url_id = quote(post.url_id, safe='')
                    post.following_status = "Follow"
                    if post.contentType != "text/plain":
                        post.content = f"data:{post.contentType};charset=utf-8;base64, {post.content}"
                
                return posts

            posts = []

            # Get the posts of the people that the user follows
            for follower in following:
                user_id = follower['id']
                user_posts = get_public_posts(user_id)
                posts.extend(user_posts)

            for post in posts:
                post.likes_count = Like.objects.filter(post=post).count()
                post.url_id = quote(post.url_id, safe='')
                post.following_status = "Follow"
                if post.contentType != "text/plain":
                    post.content = f"data:{post.contentType};charset=utf-8;base64, {post.content}"
                post.following_status = "Following"

            return posts
        else:
            posts = get_all_public_posts()

            for post in posts:
                post.likes_count = Like.objects.filter(post=post).count()
                post.url_id = quote(post.url_id, safe='')
                post.following_status = False
                posts.append(post)
            
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

def get_post_likes(post_id):
    """
    Gets all likes for a post.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        post_id: The id of the post object.

    Returns:
        JsonResponse containing the likes for a post.
    """
    post = Post.objects.get(url_id=post_id)

    likes = Like.objects.filter(post=post)

    return likes

@csrf_exempt
def save_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        content_type = request.POST.get('content_type')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        image_url = request.POST.get('image_url')
        visibility = request.POST.get('visibility')

        current_user = request.user
        current_user_model = get_object_or_404(User, user=current_user)
        
        # Ensure that either content, image, or image URL is provided
        if not content_type and not image and not image_url:
            return JsonResponse({'error': 'Post content is required.'}, status=400)

        # Determine content type and set appropriate content
        if content:
            content_type = 'text/plain'
            post_content = content
        elif image:
            image_data = image.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            image_content = image.content_type.split('/')[1]
            content_type = 'image/' + image_content
            post_content = encoded_image
        elif image_url:
            print(image_url)
            image_content = image_url.split('.')[-1]
            content_type = 'image/' + image_content
            try:
                with urlopen(image_url) as url:
                    f = url.read()
                    encoded_string = base64.b64encode(f).decode("utf-8")
            except Exception as e:
                raise ValueError(f"Failed to retrieve image from URL: {e}")
            post_content = encoded_string
        else:
            return JsonResponse({'error': 'Invalid post data.'}, status=400)
        
        post = Post(
            user=current_user_model,
            title=title,
            description=description,
            content=post_content,
            contentType=content_type,
            visibility=visibility,
        )

        post.save()

        return redirect('/chartreuse/homepage/')
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def follow_user(request):
    """
    Follow a user.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        follower_id: The id of the user who is following.
        following_id: The id of the user who is being followed.

    Returns:
        JsonResponse containing the follower object.
    """
    body = json.loads(request.body)
    user_id = body["user_id"]
    post_id = body["post_id"]

    user = User.objects.get(url_id=unquote(user_id))
    post = Post.objects.get(url_id=unquote(post_id))

    post_author = post.user

    # first check if the user has already followed the author
    follow = Follow.objects.filter(follower=user, followed=post_author)

    follow_status = None

    if follow:
        follow.delete()
        follow_status = "False"
    else:
        Follow.objects.create(follower=user, followed=post_author)
        follow_status = "True"
    
    print(follow_status)

    return JsonResponse({"following_status": follow_status})

def like_post(request):
    """
    Like a post.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        user_id: The id of the user who liked the post.
        post_id: The id of the post object.

    Returns:
        JsonResponse containing the post object.
    """
    body = json.loads(request.body)
    user_id = body["user_id"]
    post_id = body["post_id"]

    user = User.objects.get(url_id=unquote(user_id))
    post = Post.objects.get(url_id=unquote(post_id))

    # first check if the user has already liked the post
    like = Like.objects.filter(user=user, post=post)

    if like:
        like.delete()
    else:
        Like.objects.create(user=user, post=post)

    data = {
        "likes_count": get_post_likes(unquote(post_id)).count()
    }
    return JsonResponse(data)

def get_all_public_posts():
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
        user = follower.followed
        follower_attributes = {
            "type": "author",
            "id": user.url_id,
            "host": user.host,
            "displayName": user.displayName,
            "page": user.url_id,
            "github": user.github,
            "profileImage": user.profileImage
        }
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
    author = User.objects.get(url_id=user_id)

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