import base64
import json
import re
from urllib.parse import unquote,quote
from urllib.request import urlopen

from chartreuse.models import Like, Post, User, Node, Follow
from chartreuse.views import Host
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action, api_view
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ChunkedEncodingError

def get_post_likes(post_id):
    """
    Gets all likes for a post.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        post_id: The id of the post object.

    Returns:
        JsonResponse containing the likes for a post.
    """
    post = Post.objects.filter(url_id=post_id).first()

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
        print(current_user,'HELLLLO')
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

            send_post_to_inbox(post_id)
        
    return redirect('/chartreuse/homepage/')

def send_post_to_inbox(post_url_id):
    post = Post.objects.get(url_id=post_url_id)
    print(post.url_id,'HERE IS URLID    Yass')
    # send this to the inbox of other nodes
    nodes = Node.objects.filter(follow_status='OUTGOING', status='ENABLED')
    
    if not nodes.exists():
        return []
    
    for node in nodes:
        host = node.host
        username = node.username
        password = node.password

        url = host
        
        url += 'authors/'

        base_url = f"{post.user.host}authors/"
        post_json_url = f"{base_url}{quote(post.user.url_id, safe='')}/posts/{quote(post.url_id, safe='')}/"
        post_response = requests.get(post_json_url)
        post_json = post_response.json()
        print(post_json,'ETHANS POST JSON FRIENDS')


        followers = Follow.objects.filter(followed = post.user)
        for follower in followers:
            if follower.follower.host == host:
                author_url_id = follower.follower.url_id
                full_url = url + f"{unquote(author_url_id).split('/')[-1]}/inbox"
                

                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "X-Original-Host": post.user.host
                }

                # send to inbox
                try:
                    requests.post(full_url, headers=headers, json=post_json, auth=(username, password))
                    # Resource: https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
                    # Stack Overflow Post: 'correct way to try/except using Python requests module'
                    # Purpose: Learned how to import the ChunckedEncodingError as defined...
                    # Hint for importing requests.exceptions as seen by: Jonathon Reinhart's Answer on May 12, 2013
                except ChunkedEncodingError: # some kind of chunked error that occurs if user is gone...
                    continue

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

        # Determine content type and set appropriate content
        # add option for commonmark here
        if (content_type == 'text') and content:
            content_type = 'text/plain'
            post_content = content

        elif (content_type == 'commonmark') and content:
            content_type = 'text/markdown'    
            post_content = content

        elif image:
            image_data = image.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            image_content = image.content_type.split('/')[1]
            if image_content not in ['jpeg', 'png', 'jpg']:
                image_content = 'png'
            content_type = 'image/' + image_content + ';base64'
            post_content = encoded_image
        elif image_url:
            image_content = image_url.split('.')[-1]
            if image_content not in ['jpeg', 'png', 'jpg']:
                image_content = 'png'
            content_type = 'image/' + image_content + ';base64'
            try:
                with urlopen(image_url) as url:
                    f = url.read()
                    encoded_string = base64.b64encode(f).decode("utf-8")
            except Exception as e:
                raise ValueError(f"Failed to retrieve image from URL: {e}")
            post_content = encoded_string
        else:
            return JsonResponse({'error': 'Invalid post data.'}, status=400)
        
        post = Post.objects.filter(url_id=unquote(post_id)).first()
        if (post.user != current_user_model):
            return JsonResponse({'error': 'Unauthorized access.'}, status=401)

        post.title = title
        post.description = description
        post.content = post_content
        post.contentType = content_type
        post.visibility = visibility

        post.save()

        send_post_to_inbox(post.url_id)

        return redirect('/chartreuse/homepage/post/' + post_id + '/')
    return redirect('/chartreuse/error/')

@extend_schema(
    summary="Repost an existing post",
    description=(
        "Allows an authenticated user to create a repost of an existing post by providing necessary details. "
        "The `content_type` must be explicitly set to `repost` to identify the action as a repost.\n\n"
        "**When to use:** Use this endpoint when a user wants to share or repost an existing post with their own "
        "optional title and description.\n\n"
        "**How to use:** Send a POST request with a JSON body containing the following keys:\n"
        "- `title`: Optional title for the repost.\n"
        "- `content_type`: Must be `repost`.\n"
        "- `content`: The URL or text being reposted.\n"
        "- `description`: Optional description for the repost.\n\n"
        "**Why to use:** This endpoint creates a new post entry for the user, representing their repost of the original content.\n\n"
        "**Why not to use:** Avoid using if the `content_type` is not `repost` or the provided data does not align with reposting requirements."
    ),
    request=inline_serializer(
        name="RepostRequest",
        fields={
            "title": serializers.CharField(
                required=False,
                help_text="An optional title for the repost.",
                allow_blank=True
            ),
            "content_type": serializers.ChoiceField(
                choices=["repost"],
                help_text="The content type of the post, must be set to `repost`."
            ),
            "content": serializers.CharField(
                help_text="The content being reposted, such as a URL or text."
            ),
            "description": serializers.CharField(
                required=False,
                help_text="An optional description for the repost.",
                allow_blank=True
            )
        }
    ),
    responses={
        200: OpenApiResponse(
            description="Repost created successfully.",
            response=inline_serializer(
                name="RepostSuccessResponse",
                fields={
                    "success": serializers.CharField(default="You have successfully reposted this post!")
                }
            )
        ),
        400: OpenApiResponse(
            description="Invalid repost request. `content_type` must be `repost`.",
            response=inline_serializer(
                name="InvalidRepostResponse",
                fields={
                    "error": serializers.CharField(default="Can not process a non-repost.")
                }
            )
        ),
        405: OpenApiResponse(
            description="Method not allowed. Only POST requests are supported.",
            response=inline_serializer(
                name="MethodNotAllowedResponse",
                fields={
                    "error": serializers.CharField(default="Invalid request method.")
                }
            )
        ),
    }
)
@action(detail=True, methods=("POST",))
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



        repost = Post.objects.create(
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
            content_type = 'text/markdown'
            post_content = content 
        
        elif image:
            image_data = image.read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            image_content = image.content_type.split('/')[1]
            if image_content not in ['jpeg', 'png', 'jpg']:
                image_content = 'png'
            content_type = 'image/' + image_content + ';base64,'
            post_content = f'data:{content_type}{encoded_image},'
        elif image_url:
            image_content = image_url.split('.')[-1]
            if image_content not in ['jpeg', 'png', 'jpg']:
                image_content = 'png'
            content_type = 'image/' + image_content +';base64,'
            try:
                with urlopen(image_url) as url:
                    f = url.read()
                    encoded_string = base64.b64encode(f).decode("utf-8")
            except Exception as e:
                raise ValueError(f"Failed to retrieve image from URL: {e}")
            post_content = f'data:{content_type}{encoded_string},'
        else:
            return JsonResponse({'error': 'Invalid post data.'}, status=400)
        
        post = Post.objects.create(
            user=current_user_model,
            title=title,
            description=description,
            content=post_content,
            contentType=content_type,
            visibility=visibility,
        )

        post.save()

        

        send_post_to_inbox(post.url_id)

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
        post = Post.objects.filter(url_id=unquote(post_id)).first()

        # first check if the user has already liked the post
        like = Like.objects.filter(user=user, post=post).first()

        if like:
            send_like_to_inbox(like.url_id)
            like.delete()
        else:
            newLike = Like.objects.create(user=user, post=post)
            newLike.save()

            send_like_to_inbox(newLike.url_id)

        data = {
            "likes_count": get_post_likes(unquote(post_id)).count()
        }
        return JsonResponse(data)
    else:
        pass

def send_like_to_inbox(like_url_id):
    like = Like.objects.get(url_id=like_url_id)
    # send this to the inbox of other nodes
    if like.comment is None or like.comment == '':
        obj_hostname = like.post.user.host
        like_type = "POST"
    else:
        obj_hostname = like.comment.user.host
        like_type = "COMMENT"

 
    
    if like_type == "POST":
        if like.user.host == like.post.user.host:
            nodes = Node.objects.filter(follow_status='OUTGOING', status='ENABLED')
            if not nodes.exists():
                return []
            
            all_outgoing = set()
            for node in nodes:
                all_outgoing.add(node.host)
                
            post_owner_follows = Follow.objects.filter(followed=like.post.user)
            follow_hosts = set()
            for follow in post_owner_follows:
                if follow.follower.host in all_outgoing:
                    follow_hosts.add(follow.follower.host)
            node_objs = {}
            for hostname in follow_hosts:
                node_objs[hostname] = list()
            
            for follow in post_owner_follows:
                if follow.follower.host in node_objs:
                    node_objs[follow.follower.host].append(follow.follower.url_id)

        else:
            post_owner_host = like.post.user.host
            node_objs = {}
            node_queryset = Node.objects.filter(host=post_owner_host,status='ENABLED',follow_status="OUTGOING")
            if node_queryset.exists():
                node_objs[node_queryset[0].host] = [like.post.user.url_id]
    else:
        # this is a comment like.....
        if like.user.host == like.comment.user.host:
            nodes = Node.objects.filter(follow_status='OUTGOING', status='ENABLED')
            if not nodes.exists():
                return []
            
            if like.comment.user.host == like.comment.post.user.host:
                # send the comment like to all the post owners followers!
                all_outgoing = set()
                for node in nodes:
                    all_outgoing.add(node.host)
                    
                post_owner_follows = Follow.objects.filter(followed=like.comment.post.user)
                follow_hosts = set()
                for follow in post_owner_follows:
                    if follow.follower.host in all_outgoing:
                        follow_hosts.add(follow.follower.host)
                node_objs = {}
                for hostname in follow_hosts:
                    node_objs[hostname] = list()
                
                for follow in post_owner_follows:
                    if follow.follower.host in node_objs:
                        node_objs[follow.follower.host].append(follow.follower.url_id)
                
            
            else:
                post_owner_host = like.comment.post.user.host
                node_objs = {}
                node_queryset = Node.objects.filter(host=post_owner_host,status="ENABLED",follow_status="OUTGOING")
                if node_queryset.exists():
                    node_objs[node_queryset[0].host] = [like.comment.post.user.url_id]

        else:
            # case when local user likes the comment of another node's user!
            comment_owner_host = like.comment.user.host
            node_objs = {}
            node_queryset = Node.objects.filter(host=comment_owner_host,status='ENABLED',follow_status="OUTGOING")
            if node_queryset.exists():
                node_objs[node_queryset[0].host] = [like.comment.user.url_id]
    
    base_url = f"{like.user.host}authors/"
    likes_json_url = f"{base_url}{quote(like.user.url_id, safe='')}/liked/{quote(like.url_id, safe='')}/"

    likes_response = requests.get(likes_json_url)
    likes_json = likes_response.json()

    for node in node_objs:
        # author_url_id = like.user.url_id
        
        node_copy = Node.objects.get(host=node,follow_status='OUTGOING')
        for to_send_id in node_objs[node]:
        
            username = node_copy.username
            password = node_copy.password

            url = node
            
            url += 'authors/'

            url += f"{unquote(to_send_id).split('/')[-1]}/inbox"

            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "X-Original-Host": like.user.host
            }
            
        # send to inbox
        try:
            requests.post(url, headers=headers, json=likes_json, auth=(username, password))
        except Exception as e:
            return JsonResponse({'error': 'Failed to send comment to inbox.'})

    return JsonResponse({"status": "Like added successfully"})

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
    
def prepare_posts(posts):
    '''
    Purpose: to add the current like count to the post and percent encode their ids to allow for navigation to the post.

    Arguments:
    posts: list of post objects
    '''
    prepared = []
    for post in posts:
        if post.contentType == "repost":
            post.content = unquote(post.content)
            original_post = Post.objects.get(url_id=post.content)

            repost_time = post.published
                
                
            repost_user = post.user
            repost_url = post.url_id

            post = original_post

            post.repost = True
            post.repost_user = repost_user
            post.repost_url = repost_url
            post.likes_count = Like.objects.filter(post=original_post).count()
            post.repost_time = repost_time
            post.user.profileImage = get_image_post(post.user.profileImage)

        else:
            post.likes_count = Like.objects.filter(post=post).count()
               
                
        if (post.contentType != "text/plain") and (post.contentType != "text/markdown"):
            if not post.content.startswith('data:'):
                post.content = f"data:{post.contentType};charset=utf-8;base64, {post.content}"
        post.url_id = quote(post.url_id,safe='')
            
        prepared.append(post)
        
    return prepared
