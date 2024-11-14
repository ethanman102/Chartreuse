from urllib.parse import unquote
from ..models import Like, User, Post, Comment, FollowRequest
from ..views import Host
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def inbox(request, user_id):
    decoded_user_id = unquote(user_id)

    user = User.objects.get(pk=decoded_user_id)

    data = json.loads(request.body.decode('utf-8'))

    if (data["type"] == "post"):
        title = data["title"]
        description = data["description"]
        post_id = data["id"]
        contentType = data["contentType"]
        content = data["content"]
        author = data["author"]
        comments = data["comments"]
        likes = data["likes"]
        published = data["published"]
        visibility = data["visibility"]

        # check whether we need to add this post or update it or delete it
        post = Post.objects.filter(url_id=post_id)
        print(data)

        if len(post) == 0:
            # get author object
            author_id = unquote(author["id"])
            author = User.objects.get(pk=author_id)

            # create a new post
            new_post = Post.objects.create(title=title, description=description, contentType=contentType, content=content, user=author, published=published, visibility=visibility)
            new_post.save()

            # add comment objects
            post_comments = comments["src"]
            for post_comment in post_comments:
                comment_author = post_comment["author"]
                comment = post_comment["comment"]
                contentType = post_comment["contentType"]
                comment_id = post_comment["id"]
                post = post_comment["post"]
                published = post_comment["published"]
                likes = post_comment["likes"]

                comment_author_id = unquote(comment_author["id"])
                comment_author = User.objects.get(pk=comment_author_id)

                new_comment = Comment.objects.create(user=comment_author, comment=comment, contentType=contentType, post=new_post, dateCreated=published)
                new_comment.save()

                # add comment likes
                comment_likes = likes["src"]
                for comment_like in comment_likes:
                    like_author = comment_like["author"]
                    published = comment_like["published"]
                    like_id = comment_like["id"]
                    post = comment_like["object"]

                    like_author_id = unquote(like_author["id"])
                    like_author = User.objects.get(pk=like_author_id)

                    new_like = Like.objects.create(user=like_author, published=published, comment=new_comment)
                    new_like.save()

            # add like objects
            post_likes = likes["src"]
            for post_like in post_likes:
                author = post_like["author"]
                published = post_like["published"]
                like_id = post_like["id"]
                post = post_like["object"]

                new_like = Like.objects.create(author=author, published=published, post=new_post)
                new_like.save()
                
        return JsonResponse({"status": "Post added successfully"})

    elif (data["type"] == "comment"):
        comment_author = data["author"]
        comment = data["comment"]
        contentType = data["contentType"]
        comment_id = data["id"]
        post = data["post"]
        published = data["published"]
        likes = data["likes"]
        # add this new comment if it does not exist, if it exists, then delete it

        comment_author_id = unquote(comment_author["id"])
        comment_author = User.objects.get(pk=comment_author_id)

        new_comment = Comment.objects.create(user=comment_author, comment=comment, contentType=contentType, post=new_post, dateCreated=published)
        new_comment.save()

        # add comment likes
        comment_likes = likes["src"]
        for comment_like in comment_likes:
            like_author = comment_like["author"]
            published = comment_like["published"]
            like_id = comment_like["id"]
            post = comment_like["object"]

            like_author_id = unquote(like_author["id"])
            like_author = User.objects.get(pk=like_author_id)

            new_like = Like.objects.create(user=like_author, published=published, comment=new_comment)
            new_like.save()
        
    elif (data["type"] == "like"):
        author = data["author"]
        published = data["published"]
        like_id = data["id"]
        post = data["object"]
        # add the like if it does not exist, if it exists, delete the like

        author_id = unquote(author["id"])
        author = User.objects.get(pk=author_id)

        post_id = unquote(post["id"])
        post = Post.objects.get(url_id=post_id)

        new_like = Like.objects.create(user=author, published=published, post=post) 
        new_like.save()

    elif (data["type"] == "follow"):
        actor = data["actor"]
        object_to_follow = data["object"]

        follower = User.objects.get(pk=unquote(actor["id"]))
        followed = User.objects.get(pk=unquote(object_to_follow["id"]))

        # add the follow request if it does not exist, if it exists, delete the follow request
        new_follow_request = FollowRequest.objects.create(follower=follower, followed=followed)
        new_follow_request.save()