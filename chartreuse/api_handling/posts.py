from django.http import JsonResponse
from django.core.paginator import Paginator
from ..models import User, Like, Post, Follow, Comment
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from . import users
import json

def create_post(request, user_id):
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

        # Pagination setup
        page = request.GET.get('page', 1)
        size = request.GET.get('size', 50)

        author = get_object_or_404(User, id=user_id)
        posts = Post.objects.filter(user=author).latest("published")

        response = users.user(request, user_id)

        data = json.loads(response.content)

        posts_paginator = Paginator(posts, size)

        page_posts = posts_paginator.page(page)

        author_posts = []

        for post in page_posts:
            
            if post.visibility == "PUBLIC":
                postObject = {
                    "type":"post",
                    "title":post.title,
                    "id": post.id,
                    "description":post.description,
                    "contentType":post.contentType,
                    "content":post.content,
                    "author":{
                        "type":"author",
                        "id":data["id"],
                        "host":data["host"],
                        "displayName":data["displayName"],
                        "page":data["page"],
                        "github":data["github"],
                        "profileImage":data["profileImage"]
                    },
                    # TODO
                    "comments":{
                        "type":"comments",
                        # TODO
                        "page":None,
                        # TODO
                        "id":None,
                        "page_number":None,
                        "size":None,
                        "count":None,
                        "src":[
                            {
                            "type":"comment"
                            }
                        ]
                    },
                    #TODO
                    "likes":{
                        "type":"likes",
                        "page":"http://nodeaaaa/authors/222/posts/249",
                        "id":"http://nodeaaaa/api/authors/222/posts/249/likes",
                        "page_number":1,
                        "size":50,
                        "count": 9001,
                        "src":[
                            {
                                "type":"like",
                                "author":{
                                    "type":"author",
                                    "id":"http://nodeaaaa/api/authors/111",
                                    "page":"http://nodeaaaa/authors/greg",
                                    "host":"http://nodeaaaa/api/",
                                    "displayName":"Greg Johnson",
                                    "github": "http://github.com/gjohnson",
                                    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                                },
                                "published":"2015-03-09T13:07:04+00:00",
                                "id":"http://nodeaaaa/api/authors/111/liked/166",
                                "object": "http://nodebbbb/authors/222/posts/249"
                            }
                        ]
                    },
                    "published":post.published,
                    "visibility":"PUBLIC"
                }
                author_posts.append(postObject)

            elif post.visibility == "FRIENDS":
                postObject = {
                    "type":"post",
                    "title":post.title,
                    # TODO: find out the id
                    "id": None,
                    "page":None,
                    "description":post.description,
                    "contentType":post.contentType,
                    "content":post.content,
                    "author":{
                        "type":"author",
                        "id":data["id"],
                        "host":data["host"],
                        "displayName":data["displayName"],
                        "page":data["page"],
                        "github":data["github"],
                        "profileImage":data["profileImage"]
                    },
                    # TODO
                    "comments":{
                        "type":"comments",
                        # TODO
                        "id":None,
                        # TODO
                        "page":None,
                        "page_number":None,
                        "size":None,
                        "count":None,
                        "src":[]
                    },
                    #TODO
                    "likes":{
                        "type":"likes",
                        "id":"http://nodeaaaa/api/authors/222/posts/249/likes",
                        "page":"http://nodeaaaa/authors/222/posts/249",
                        "page_number":1,
                        "size":50,
                        "count": 9001,
                        "src":[]
                    },
                    "published":post.published,
                    "visibility":"FRIENDS"
                }
                author_posts.append(postObject)

        return JsonResponse(author_posts)
    
    if request.method == "POST":
        # Ensure the user creating the post is the current user
        author = get_object_or_404(User, id=user_id)

        # Create and save the post
        Post.objects.create(title=request.POST.get('title'), user=author, description=request.POST.get('description'), contentType = request.POST.get('contentType'), content = request.POST.get('content'), visibility = request.POST.get('visibility'))
        return JsonResponse({"message": "Post created"}, status=201)

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)
    
def update_post(request, user_id, post_id):
    """
    Gets, deletes, or updates the post requested
    
    Parameters:
        request: HttpRequest object containing the request and query parameters.
        user_id: The id of the user who is creating or created the post.
        post_id: The id of the post being updated / requested / deleted
        
    Returns:
        JsonResponce containing response 
    """
    if request.method == "GET":
        post = get_object_or_404(Post, id=post_id)

        response = users.user(request, user_id)
        data = json.loads(response.content)

        if post.visibility == "FRIENDS":
            # ensure the user is a friend of the author
            user = get_object_or_404(User, id=user_id)
            author = post.user
            follow = get_object_or_404(Follow, followed = author, follower = user)

            # get the first page of comments
            comments = Comment.objects.filter(post=post)
            num_comments = 5
            comment_count = len(comments)
            comment_list = []
            for comment in comments[0:num_comments]:
                # TODO: get the comment likes
                # for like in comment.likes
                comment_like_count = 0

                comment_list.append({
                    "type":"comment",
                    "author":{
                        "type":"author",
                        "id":data["id"],
                        "page":data["page"],
                        "host":data["host"],
                        "displayName":data["displayName"],
                        "github": data["github"],
                        "profileImage": data["profileImage"]
                    },
                    "comment":comment.comment,
                    "contentType":comment.commentType,
                    "published":comment.dateCreated,
                    "id":str(post.user.host) + "commented/" + str(comment.id),
                    "post":post.id,
                    "page":None,
                    "likes":{
                        "type":"likes",
                        "id":str(post.user.host) + "commented/" + str(comment.id) + "likes",
                        "page":None,
                        "page_number":1,
                        "size":50,
                        "count":comment_like_count,
                        "src":[],
                    }

                    
                })

            # get the first page of likes
            likes = Like.objects.filter(post=post_id)
            like_size = 50
            like_count = len(likes)
            like_list = []

            for like in likes:
                like_author = like.user
                like_list.append(
                    {
                        "type":"like",
                        "author":{
                            "type":"author",
                            "id":like_author.host + str(like_author.user.id),
                            "page":like_author.host + str(like_author.displayName),
                            "host":like_author.host,
                            "displayName":like_author.displayName,
                            "github":like_author.github,
                            "profileImage":like_author.profileImage
                        },
                        "published":like.dateCreated,
                        "id":like_author.host + str(like_author.user.id) + "liked/" + str(post_id),
                        "object":post.id
                    }
                )

            # render and return the post object  
            postObject = {
                "type":"post",
                "title":post.title,
                "id": post.id,
                #TODO is this correct?
                "page":post.id,
                "description":post.description,
                "contentType":post.contentType,
                "content":post.content,
                "author":{
                    "type":"author",
                    "id":data["id"],
                    "host":data["host"],
                    "displayName":data["displayName"],
                    "page":data["page"],
                    "github":data["github"],
                    "profileImage":data["profileImage"]
                },
                "comments":{
                    "type":"comments",
                    "id":None,
                    "page":None,
                    "page_number":1,
                    "size":num_comments,
                    "count":len(comments),
                    "src":comment_list
                },
                "likes":{
                    "type":"likes",
                    "id":None,
                    "page":None,
                    "page_number":1,
                    "size":like_size,
                    "count":like_count,
                    "src":like_list
                },
                "published":post.published,
                "visibility":"FRIENDS"
            }    
            return JsonResponse(postObject)

        if post.visibility == "PUBLIC":
            # get the first page of comments
            comments = Comment.objects.filter(post=post)
            num_comments = 5
            comment_count = len(comments)
            comment_list = []
            for comment in comments[0:num_comments]:
                # TODO: get the comment likes
                # for like in comment.likes
                comment_like_count = 0
                comment_author = comment.user

                comment_list.append({
                    "type":"comment",
                    "author":{
                        "type":"author",
                        "id":comment_author.id,
                        "page":comment_author.host + "authors/" + comment_author.displayName,
                        "host":comment_author.host,
                        "displayName":comment_author.displayName,
                        "github":comment_author.github,
                        "profileImage":comment_author.profileImage
                    },
                    "comment":comment.comment,
                    "contentType":comment.commentType,
                    "published":comment.dateCreated,
                    "id":str(post.user.host) + "commented/" + str(comment.id),
                    "post":post.id,
                    "page":None,
                    "likes":{
                        "type":"likes",
                        "id":str(post.user.host) + "commented/" + str(comment.id) + "likes",
                        "page":None,
                        "page_number":1,
                        "size":50,
                        "count":comment_like_count,
                        "src":[],
                    }

                    
                })

            # get the first page of likes
            likes = Like.objects.filter(post=post_id)
            like_size = 50
            like_count = len(likes)
            like_list = []

            for like in likes:
                like_author = like.user
                like_list.append(
                    {
                        "type":"like",
                        "author":{
                            "type":"author",
                            "id":like_author.host + str(like_author.user.id),
                            "page":like_author.host + str(like_author.displayName),
                            "host":like_author.host,
                            "displayName":like_author.displayName,
                            "github":like_author.github,
                            "profileImage":like_author.profileImage
                        },
                        "published":like.dateCreated,
                        "id":like_author.host + str(like_author.user.id) + "liked/" + str(post_id),
                        "object":post.id
                    }
                )
            postObject = {
                "type":"post",
                "title":post.title,
                "id":post.id,
                "description":post.description,
                "contentType":post.contentType,
                "content":post.content,
                "author":{
                    "type":"author",
                    "id":data["id"],
                    "host":data["host"],
                    "displayName":data["displayName"],
                    "page":data["page"],
                    "github":data["github"],
                    "profileImage":data["profileImage"]
                },
                
                "comments":{
                    "type":"comments",
                    # TODO
                    "page":None,
                    # TODO
                    "id":None,
                    "page_number":None,
                    "size":None,
                    "count":None,
                    "src":[
                        {
                        "type":"comment"
                        }
                    ]
                },
                #TODO
                "likes":{
                    "type":"likes",
                    "page":"http://nodeaaaa/authors/222/posts/249",
                    "id":"http://nodeaaaa/api/authors/222/posts/249/likes",
                    "page_number":1,
                    "size":50,
                    "count": 9001,
                    "src":[
                        {
                            "type":"like",
                            "author":{
                                "type":"author",
                                "id":"http://nodeaaaa/api/authors/111",
                                "page":"http://nodeaaaa/authors/greg",
                                "host":"http://nodeaaaa/api/",
                                "displayName":"Greg Johnson",
                                "github": "http://github.com/gjohnson",
                                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
                            },
                            "published":"2015-03-09T13:07:04+00:00",
                            "id":"http://nodeaaaa/api/authors/111/liked/166",
                            "object": "http://nodebbbb/authors/222/posts/249"
                        }
                    ]
                },
                "published":post.published,
                "visibility":"PUBLIC"
            }
            return JsonResponse(postObject)
        
        if post.visibility == "UNLISTED":
            pass

        else:
            return JsonResponse({"error":"Post not found"}, status=404)

    if request.method == "DELETE":
        # Ensure the user deleting the post is the author
        author = get_object_or_404(User, id=user_id)

        post = get_object_or_404(Post, id=post_id)
        post.visibility = "DELETED"

        return JsonResponse({"message":"post deleted"}, status=204)

    if request.method == "PUT":
        # Ensure the user editing the post is the author
        author = get_object_or_404(User, id=user_id)

        # edit the post attributes
        raise NotImplementedError
        return JsonResponse(postObject)

        
    