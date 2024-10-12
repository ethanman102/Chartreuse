from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import User, FollowRequest, Follow
from django.contrib.auth.decorators import login_required
from urllib.parse import unquote

@login_required
def send_follow_request(request, author_id):
    '''
    Handles sending a follow request to an author.

    Parameters:
        request: HttpRequest object containing the request.
        author_id: The id of the author to send the follow request to.

    Returns:
        JsonResponse with the follow request details.
    '''
    if request.method == 'POST':
        current_user = User.objects.get(user=request.user)
        author = get_object_or_404(User, id=author_id)

        # Check if a follow request already exists
        if FollowRequest.objects.filter(requester=current_user, requestee=author).exists():
            return JsonResponse({"error": "Follow request already sent."}, status=400)

        # Create and save a follow request
        follow_request = FollowRequest(requester=current_user, requestee=author)
        follow_request.save()

        return JsonResponse({"message": "Follow request sent."}, status=200)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@login_required
def accept_follow_request(request, request_id):
    '''
    Accepts a follow request.

    Parameters:
        request: HttpRequest object containing the request.
        request_id: The id of the follow request to accept.

    Returns:
        JsonResponse with success message.
    '''
    if request.method == 'POST':
        follow_request = get_object_or_404(FollowRequest, id=request_id)

        # Create a follower object
        follower = Follow(follower=follow_request.requester, followed=follow_request.requestee)
        follower.save()

        # Delete the follow request
        follow_request.delete()

        return JsonResponse({"message": "Follow request accepted."}, status=200)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@login_required
def reject_follow_request(request, request_id):
    '''
    Rejects a follow request.

    Parameters:
        request: HttpRequest object containing the request.
        request_id: The id of the follow request to reject.

    Returns:
        JsonResponse with success message.
    '''
    if request.method == 'DELETE':
        follow_request = get_object_or_404(FollowRequest, id=request_id)

        # Delete the follow request
        follow_request.delete()

        return JsonResponse({"message": "Follow request rejected."}, status=200)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)


@login_required
def get_follow_requests(request):
    '''
    Retrieves the list of pending follow requests for the logged-in user.

    Parameters:
        request: HttpRequest object containing the request.

    Returns:
        JsonResponse with the list of follow requests.
    '''
    author = User.objects.get(user=request.user)

    follow_requests = FollowRequest.objects.filter(requestee=author, approved=False)

    requests_list = [
        {
            "type": "follow",
            "summary": f"{follow_request.requester.displayName} wants to follow {follow_request.requestee.displayName}",
            "actor": {
                "type": "author",
                "id": f"{follow_request.requester.host}/authors/{follow_request.requester.id}",
                "host": follow_request.requester.host,
                "displayName": follow_request.requester.displayName,
                "github": follow_request.requester.github,
                "profileImage": follow_request.requester.profileImage
            },
            "object": {
                "type": "author",
                "id": f"{follow_request.requestee.host}/authors/{follow_request.requestee.id}",
                "host": follow_request.requestee.host,
                "displayName": follow_request.requestee.displayName,
                "github": follow_request.requestee.github,
                "profileImage": follow_request.requestee.profileImage
            }
        }
        for follow_request in follow_requests
    ]

    return JsonResponse({"follow_requests": requests_list}, status=200)
