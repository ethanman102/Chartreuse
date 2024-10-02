from django.http import JsonResponse
from django.core.paginator import Paginator
from ..models import User, Like
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from . import users
import json

def post(request, user_id):
    """
    Creates a new post or gets the most recent post from user_id
    
    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the user who is creating or created the post.
        
    Returns:
        JsonResponce containing the most recent posts or a new post    
    """
    if request.method == "GET":
        # Get the most recent posts from author
        pass

    if request.method == "POST":
        pass

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)