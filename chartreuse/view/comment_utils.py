import json
from urllib.parse import quote, unquote

from chartreuse.models import Comment, Like, Post, User, Node, Follow
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
import requests

def add_comment(request):
    try:
        if request.user.is_authenticated:
            body = json.loads(request.body)
            user_id = body["user_id"]
            post_id = body["post_id"]

            user = User.objects.get(url_id=unquote(user_id))
            post = Post.objects.get(url_id=unquote(post_id))
            
            # Parse the JSON body to get the comment text and content type
            body = json.loads(request.body)
            comment_text = body.get('comment', '')
            content_type = body.get('contentType', 'text/plain')

            # Create and save the comment
            if (comment_text != ""):
                comment = Comment(user=user, post=post, comment=comment_text, contentType=content_type)
                comment.save()

                send_comment_to_inbox(comment.url_id)

            return JsonResponse({'success': 'Comment added successfully.'})
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def get_comments(post_id):
    '''
    Purpose: Get all comments for a post

    Arguments:
        request: Request object
        post_id: The id of the post object
    '''
    post_id = unquote(post_id)
    post = Post.objects.get(url_id=post_id)

    comments = Comment.objects.filter(post=post).order_by('-dateCreated')

    return comments

def like_comment(request):
    """
    Like a comment.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        user_id: The id of the user who liked the comment.
        comment_id: The id of the comment object.

    Returns:
        JsonResponse containing the comment object.
    """
    if request.user.is_authenticated:
        body = json.loads(request.body)
        user_id = body["user_id"]
        comment_id = body["comment_id"]

        user = User.objects.get(url_id=unquote(user_id))
        comment = Comment.objects.get(url_id=unquote(comment_id))

        # first check if the user has already liked the comment
        like = Like.objects.filter(user=user, comment=comment)

        if like:
            like.delete()
        else:
            newLike = Like.objects.create(user=user, comment=comment)
            newLike.save()

        data = {
            "likes_count": get_comment_likes(unquote(comment_id)).count()
        }

        send_comment_to_inbox(comment.url_id)

        return JsonResponse(data)
    else:
        pass

def get_comment_likes(comment_id):
    """
    Gets all likes for a comment.

    Parameters:
        request: rest_framework object containing the request and query parameters.
        comment_id: The id of the comment object.

    Returns:
        JsonResponse containing the likes for a comment.
    """
    comment = Comment.objects.get(url_id=comment_id)

    likes = Like.objects.filter(comment=comment)

    return likes

def delete_comment(request, comment_id):
    '''
    Purpose: View to delete a comment

    Arguments:
        request: Request object
        comment_id: The id of the comment object
    '''
    comment = get_object_or_404(Comment, url_id=comment_id)

    # Check if user is authenticated
    if request.user.is_authenticated:
        current_user = request.user
        current_user_model = get_object_or_404(User, user=current_user)
        
        # Check if the current user is the author of the comment
        if current_user_model == comment.user:
            comment.delete()
        
        post = comment.post
        post_id = quote(post.url_id, safe='')
    
    return redirect('/chartreuse/homepage/post/' + post_id + '/')

def send_comment_to_inbox(comment_url_id):
    comment = Comment.objects.get(url_id=comment_url_id)
    # send this to the inbox of other nodes
    nodes = Node.objects.filter(follow_status='OUTGOING')

    if not nodes.exists():
        return []
    
    base_url = f"{comment.user.host}authors/"
    comments_json_url = f"{base_url}{quote(comment.post.user.url_id, safe='')}/posts/{quote(comment.post.url_id, safe='')}/comment/{quote(comment.url_id, safe='')}/"

    comments_response = requests.get(comments_json_url)
    comments_json = comments_response.json()

    followers = Follow.objects.filter(followed = comment.post.user)
    print("FOLLOWERS", followers)
    for follower in followers:
        print("FOLLOWER", follower.follower)
        print("FOLLOWED", follower.followed)
        if follower.follower.host != comment.user.host:
            print("FOLLOWER (true)", follower.follower.host)
            author_url_id = follower.follower.url_id
            node = Node.objects.get(host=follower.follower.host)
            print("NODE", node.host)
            host = node.host
            username = node.username
            password = node.password

            url = host
            
            url += 'authors/'

            url += f'{quote(author_url_id, safe = "")}/inbox/'

            headers = {
                'Authorization' : f'Basic {username}:{password}',
                "Content-Type": "application/json; charset=utf-8"
            }
            print("SENT COMMENT", comments_json)
            print("URL", url)

            # send to inbox
            requests.post(url, headers=headers, json=comments_json)
    
    return JsonResponse({'status': 'Comment sent to inbox successfully.'})