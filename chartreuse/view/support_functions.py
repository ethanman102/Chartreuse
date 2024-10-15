from django.shortcuts import get_object_or_404
from chartreuse.models import User, Post, Follow, Like
from urllib.parse import unquote
from django.shortcuts import redirect, render
from django.http import JsonResponse
import json

import base64
from urllib.request import urlopen
from django.http import JsonResponse
from urllib.parse import unquote
from django.views.decorators.csrf import csrf_exempt

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

def add_post(request):
    return render(request, 'add_post.html')

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
        followed_list.append(user)

    return followed_list

def get_posts(user_id, post_type):
    """
    Gets all posts from a user of a specific type.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        user_id: The id of the user who created the posts.
        post_id: The id of the post object.

    Returns:
        JsonResponse containing the post object.
    """
    author = User.objects.get(url_id=user_id)

    posts = Post.objects.filter(user=author, visibility=post_type)

    return posts