import base64
import json
import re
from urllib.parse import unquote
from urllib.request import urlopen

from chartreuse.models import Like, Post, User
from chartreuse.views import Host
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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
    '''
    Purpose: View to render the add post page

    Arguments:
        request: Request object
    '''
    if request.user.is_authenticated:
        return render(request, 'add_post.html')
    else:
        return redirect('/chartreuse/signup/')

def edit_post(request, post_id):
    '''
    Purpose: View to render the edit post page
    
    Arguments:
        request: Request object
        post_id: The id of the post object
    '''
    post = get_object_or_404(Post, url_id=post_id)
    
    # Check if the user is authenticated
    if request.user.is_authenticated:
        current_user = request.user
        current_user_model = get_object_or_404(User, user=current_user)
        
        # Check if the current user is the author of the post
        if current_user_model == post.user:
            return render(request, 'edit_post.html', {'post': post})
    
    return redirect('/chartreuse/homepage/')

def delete_post(request, post_id):
    '''
    Purpose: View to delete a post

    Arguments:
        request: Request object
        post_id: The id of the post object
    '''
    post = get_object_or_404(Post, url_id=post_id)

    # Check if user is authenticated
    if request.user.is_authenticated:
        current_user = request.user
        current_user_model = get_object_or_404(User, user=current_user)
        
        # Check if the current user is the author of the post
        if current_user_model == post.user:
            post.visibility = 'DELETED'
            post.save()
    
    return redirect('/chartreuse/homepage/')

@csrf_exempt
def update_post(request, post_id):
    '''
    Purpose: View to update a post
    
    Arguments:
        request: Request object
        post_id: The id of the post object
    '''
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
    
        print(content_type)

        # Determine content type and set appropriate content
        # add option for commonmark here
        if (content_type == 'text') and content:
            content_type = 'text/plain'
            post_content = content

        elif (content_type == 'commonmark') and content:
            content_type = 'text/commonmark'    
            post_content = content

        elif image:
            image_data = image.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            image_content = image.content_type.split('/')[1]
            if image_content not in ['jpeg', 'png', 'jpg']:
                image_content = 'png'
            content_type = 'image/' + image_content
            post_content = encoded_image
        elif image_url:
            image_content = image_url.split('.')[-1]
            if image_content not in ['jpeg', 'png', 'jpg']:
                image_content = 'png'
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
        
        post = Post.objects.get(url_id=unquote(post_id))
        if (post.user != current_user_model):
            return JsonResponse({'error': 'Unauthorized access.'}, status=401)

        post.title = title
        post.description = description
        post.content = post_content
        post.contentType = content_type
        post.visibility = visibility

        post.save()

        return redirect('/chartreuse/homepage/post/' + post_id + '/')
    return redirect('/chartreuse/error/')

def repost(request):
    '''
    Purpose: API endpoint to repost a POST!

    Arguments:
        request: Request object
    '''
    if request.method == "POST":
        data = json.loads(request.body)

        title = data.get('title')

        content_type = data.get('content_type')
        if (content_type != 'repost'):
            return JsonResponse({'error':'Can not process a non-repost'},status=400)
        
        content = unquote(data.get('content'))
        
        description = data.get('description')
        reposter_auth_model = request.user
        reposter_user_model = User.objects.get(user=reposter_auth_model)



        repost = Post(
            user = reposter_user_model,
            contentType = content_type,
            description = description,
            title = title,
            content = content
        )

        repost.save()

        return JsonResponse({"success": "You have successfully reposted this post!"})
    return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@csrf_exempt
def save_post(request):
    '''
    Purpose: View to save a post

    Arguments:
        request: Request object
    '''
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
        if content and (content_type == 'text'):
            content_type = 'text/plain'
            post_content = content

        elif content and (content_type == 'repost'):
            post_content = content

        elif content and (content_type == 'commonmark'):
            content_type = 'text/commonmark'
            post_content = content 
        
        elif image:
            image_data = image.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            image_content = image.content_type.split('/')[1]
            if image_content not in ['jpeg', 'png', 'jpg']:
                image_content = 'png'
            content_type = 'image/' + image_content
            post_content = encoded_image
        elif image_url:
            image_content = image_url.split('.')[-1]
            if image_content not in ['jpeg', 'png', 'jpg']:
                image_content = 'png'
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
    if request.user.is_authenticated:
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
            newLike = Like.objects.create(user=user, post=post)
            newLike.save()

        data = {
            "likes_count": get_post_likes(unquote(post_id)).count()
        }
        return JsonResponse(data)
    else:
        pass

def get_all_public_posts():
    '''
    Retrieves all public posts.

    Returns:
        JsonResponse with the list of public posts.
    '''
    # Get all public posts
    posts = Post.objects.filter(visibility='PUBLIC')

    return posts

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

def check_duplicate_post(request):
    """
    Checks if a post with the given title, description, and content already exists for the author.

    Parameters:
        author_id: The id of the author.
        title: The title of the post.
        description: The description of the post.
        content: The content of the post.

    Returns:
        JSON response indicating whether a duplicate post exists.
    """
    if request.method == "POST":

        # Access the parameters from the JSON body
        author_id = request.POST.get("author_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        content = request.POST.get("content")

        # Decode the author_id if it's URL-encoded
        author_id = unquote(author_id)

        # Retrieve the author user object
        author = get_object_or_404(User, url_id=author_id)

        # Check for duplicates
        post_exists = Post.objects.filter(
            user=author, title=title, description=description, content=content
        ).exists()

        return JsonResponse({'exists': post_exists})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
def get_image_post(pfp_url):
    pattern = r"(?P<host>https?:\/\/.+?herokuapp\.com)\/authors\/(?P<author_serial>\d+)\/posts\/(?P<post_serial>\d+)\/image"
    match = re.search(pattern, pfp_url)

    if match:
        host = match.group("host")
        author_serial = match.group("author_serial")
        post_serial = match.group("post_serial")
    
        author = User.objects.filter(url_id=f"{host}/authors/{author_serial}").first()
        pfp_post = Post.objects.filter(user=author, url_id=f"{host}/authors/{author_serial}/posts/{post_serial}").first()

        if pfp_post and pfp_post.content and pfp_post.contentType in ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']:
            pfp_url = f"data:{pfp_post.contentType};charset=utf-8;base64, {pfp_post.content}"
        else:
            pfp_url = f"{Host.host}/static/images/default_pfp_1.png"
        return pfp_url
    else:
        return pfp_url