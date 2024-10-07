from django.http import JsonResponse
from django.core.paginator import Paginator
from ..models import User, Like, Post, Follow, Comment
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from . import users
import json

def create_comment(request, post_author_id):
    """
    Creates a new comment
    
    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the post author whos post is being commented on.
        
    Returns:
        JsonResponce containing the response   
    """
    if request.method == "POST":
        pass

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
    

def get_comments(request, post_author_id):
    """
    Gets the comments of a post
    
    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the post author whos post is being commented on.
        
    Returns:
        JsonResponce containing the response   
    """
    if request.method == "POST":
        pass

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
    

def get_comment(request, post_author_id):
    """
    Gets the comments of a post
    
    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the post author whos post is being commented on.
        
    Returns:
        JsonResponce containing the response   
    """
    if request.method == "POST":
        pass

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
    


