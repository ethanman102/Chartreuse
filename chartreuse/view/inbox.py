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
        post = Post.objects.filter(url_id=post_id).first()

        # get author object
        author_id = unquote(author["id"])
        author = User.objects.get(pk=author_id)

        if post is None:
            # create a new post
            new_post = Post.objects.create(title=title, url_id=post_id, description=description, contentType=contentType, content=content, user=author, published=published, visibility=visibility)
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

                new_comment = Comment.objects.create(user=comment_author, url_id=comment_id, comment=comment, contentType=contentType, post=new_post, dateCreated=published)
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

                    new_like = Like.objects.create(user=like_author, url_id=like_id, published=published, comment=new_comment)
                    new_like.save()

            # add like objects
            post_likes = likes["src"]
            for post_like in post_likes:
                author = post_like["author"]
                published = post_like["published"]
                like_id = post_like["id"]
                post = post_like["object"]

                new_like = Like.objects.create(author=author, url_id=like_id, published=published, post=new_post)
                new_like.save()

        else:
            # update visibility
            if visibility == "DELETED":
                post.visibility = visibility
                post.save()
            
            # update post content
            else:
                post.title = title
                post.description = description
                post.contentType = contentType
                post.content = content
                post.save()
                    
        return JsonResponse({"status": "Post added successfully"})

    elif (data["type"] == "comment"):
        comment_author = data["author"]
        comment_text = data["comment"]
        contentType = data["contentType"]
        comment_id = data["id"]
        post = data["post"]
        published = data["published"]
        likes = data["likes"]
        print("comment data", data)
        # add this new comment if it does not exist, if it exists, then delete it

        comment_author_id = unquote(comment_author["id"])
        comment_author = User.objects.get(pk=comment_author_id)

        new_post = Post.objects.get(url_id=post)

        # check whether comment already exists
        comment = Comment.objects.filter(user=comment_author, comment=comment_text, contentType=contentType, post=new_post).first()

        if comment is None:
            comment = Comment.objects.create(user=comment_author, comment=comment_text, url_id=comment_id, contentType=contentType, post=new_post, dateCreated=published)
            comment.save()

        # add comment likes
        print("likes", likes)
        comment_likes = likes["src"]
        print(comment_likes)
        for comment_like in comment_likes:
            like_author = comment_like["author"]
            published = comment_like["published"]
            like_id = comment_like["id"]
            post = comment_like["object"]
            print(like_author)
            print(like_id)

            like_author_id = unquote(like_author["id"])
            like_author = User.objects.get(pk=like_author_id)

            # check whether like already exists
            like = Like.objects.filter(user=like_author, comment=comment).first()

            print(like)
            if like is None:
                print("adding like")
                new_like = Like.objects.create(user=like_author, url_id=like_id, comment=comment, published=published)
                new_like.save()
        return JsonResponse({"status": "Comment added successfully"})
        
    elif (data["type"] == "like"):
        author = data["author"]
        published = data["published"]
        like_id = data["id"]
        post = data["object"]
        # add the like if it does not exist, if it exists, delete the like
        author_id = unquote(author["id"])
        author = User.objects.get(pk=author_id)

        post = Post.objects.get(url_id=post)

        # check whether like already exists
        like = Like.objects.filter(user=author, post=post).first()

        if like is None:
            new_like = Like.objects.create(user=author, url_id=like_id, post=post) 
            new_like.save()

            return JsonResponse({"status": "Like added successfully"})
        else:
            like.delete()

            return JsonResponse({"status": "Like removed successfully"})

    elif (data["type"] == "follow"):
        actor = data["actor"]
        object_to_follow = data["object"]

        author_queryset = User.objects.filter(url_id=unquote(actor['id'])).first()

        if not author_queryset:
            # discovered a new author to add to database...
            remote_author = User.objects.create(
                user = None,
                url_id = unquote(actor['id']),
                displayName = actor.get('displayName',''),
                host = actor.get('host'),
                github = actor.get('github',''),
                profileImage = actor.get('profileImage',''),
            )
        else:
            remote_author = author_queryset

        follower = User.objects.get(pk=unquote(actor["id"]))
        followed = User.objects.get(pk=unquote(object_to_follow["id"]))

        # add the follow request if it does not exist, if it exists, delete the follow request
        new_follow_request = FollowRequest.objects.create(requester=remote_author, requestee=followed)
        new_follow_request.save()
    
        return JsonResponse({"status": "Follow request sent successfully"},status=200)