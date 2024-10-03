from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import User, FollowRequest, Follower
from django.contrib.auth.decorators import login_required
import json

@login_required
def follow_user(request, author_id):
    