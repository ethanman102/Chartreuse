import datetime
import json
from urllib.parse import quote, unquote

from chartreuse.models import GithubPolling, Post, User
from django.http import JsonResponse
from django.shortcuts import redirect
from datetime import datetime, timedelta, timezone

def view_profile(request):
    '''
    Purpose: View to render the profile page

    Arguments:
        request: Request object
    '''
    if request.user.is_authenticated:

        current_user = request.user
        current_user_model = User.objects.get(user=current_user)
        url_id = quote(current_user_model.url_id, safe='')

        return redirect(f'/chartreuse/authors/{url_id}/')
    else:
        return redirect('/chartreuse/signup/')
    
def setNewProfileImage(request):
    '''
    Purpose: Set a new profile image
    '''
    if request.user.is_authenticated:
        body = json.loads(request.body)
        user_id = body["user_id"]
        post_id = body["post_id"]

        user = User.objects.get(url_id=unquote(user_id))
        post = Post.objects.get(url_id=unquote(post_id))

        user.profileImage = post.url_id + "/image"
        user.save()

    return JsonResponse({'success': 'Updated profile picture'}, status=200)
        
def checkGithubPolling(request):
    '''
    Purpose: Check whether we need to poll github for new events

    Arguments:
        request: Request object
    '''
    last_poll = GithubPolling.objects.last()

    if last_poll is None:
        new_poll = GithubPolling()
        new_poll.save()
        return JsonResponse({'poll': 'True'})

    time_now = datetime.now(timezone.utc)
    time_diff = time_now - last_poll.last_polled
    if time_diff > timedelta(minutes=10):
        new_poll = GithubPolling()
        new_poll.save()
        return JsonResponse({'poll': 'True'})
    else:
        return JsonResponse({'poll': 'False'})
    
