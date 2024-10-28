from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from .models import User,Like,Comment,Post,Follow,FollowRequest
from django.views.generic.detail import DetailView
from django.http import HttpResponseNotAllowed
from urllib.parse import unquote, quote


class Host():
    host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"


def error(request):
    '''
    Purpose: View to render a generic error page


    Arguments:
    request: Request object
    '''
    return render(request, 'error.html')

def test(request):
    '''
    Purpose: View to render a test page

    Test page is used for testing UI changes


    Arguments:
    request: Request object
    '''
    test_str = "# Hello and **goodbye** "
    return render(request, 'test.html', {'markdown_txt': test_str})


