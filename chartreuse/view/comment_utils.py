import json
from urllib.parse import quote, unquote

from chartreuse.models import Comment, Like, Post, User, Node, Follow
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
import requests
from .post_utils import send_like_to_inbox

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
                comment = Comment.objects.create(user=user, post=post, comment=comment_text, contentType=content_type)
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
        like = Like.objects.filter(user=user, comment=comment).first()

        if like:
            send_like_to_inbox(like.url_id)
            like.delete()
        else:
            like = Like.objects.create(user=user, comment=comment)
            like.save()
            send_like_to_inbox(like.url_id)

        data = {
            "likes_count": get_comment_likes(unquote(comment_id)).count()
        }

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
    if comment.user.host == comment.post.user.host:
        nodes = Node.objects.filter(follow_status='OUTGOING', status='ENABLED')
        all_outgoing = set()
        for node in nodes:
            all_outgoing.add(node.host)
        
        post_owner_follows = Follow.objects.filter(followed=comment.post.user)
        follow_hosts = set()
        for follow in post_owner_follows:
            if follow.follower.host in all_outgoing:
                follow_hosts.add(follow.follower.host)
        node_objs = []
        for hostname in follow_hosts:
            node_objs.append(Node.objects.get(host=hostname,status='ENABLED',follow_status='OUTGOING'))
    else:
        post_owner_host = comment.post.user.host
        node_objs = []
        node_queryset = Node.objects.filter(host=post_owner_host,status='ENABLED',follow_status="OUTGOING")
        if node_queryset.exists():
            node_objs.append(node_queryset[0])
        


    if len(node_objs) == 0:
        return []
    
    base_url = f"{comment.user.host}authors/"
    comments_json_url = f"{base_url}{quote(comment.post.user.url_id, safe='')}/posts/{quote(comment.post.url_id, safe='')}/comment/{quote(comment.url_id, safe='')}/"

    comments_response = requests.get(comments_json_url)
    comments_json = comments_response.json()

    followers = Follow.objects.filter(followed=comment.user)
    for node in node_objs:
        author_url_id = comment.post.user.url_id
        host = node.host
        username = node.username
        password = node.password

        url = host
        
        url += 'authors/'

        url += f'{quote(author_url_id, safe = "")}/inbox/'

        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }

        # send to inbox
        try:
            requests.post(url, headers=headers, json=comments_json, auth=(username, password))
            print('Comment sent to inbox successfully.')
        except Exception as e:
            print('Failed to send comment to inbox.', e)
            return JsonResponse({'error': 'Failed to send comment to inbox.'})
    
    return JsonResponse({'status': 'Comment sent to inbox successfully.'})