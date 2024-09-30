from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.db.models import UniqueConstraint

VISIBILITY_CHOICES = {"PUBLIC": "PUBLIC", "FRIENDS": "FRIENDS", "PRIVATE": "PRIVATE", "UNLISTED": "UNLISTED"}
CONTENT_TYPE_CHOICES = {"text/markdown": "text/markdown", "text/plain": "text/plain", "application/base64": "application/base64", "image/png;base64": "image/png;base64", "image/jpeg;base64": "image/jpeg;base64"}

class User(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    displayName = models.CharField(max_length=100)
    host = models.URLField()
    github = models.URLField()
    profileImage = models.URLField()
    dateCreated  = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    title = models.CharField(max_length=200)
    id = models.URLField(primary_key=True)
    description = models.TextField()
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='text/plain')
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.DateTimeField()
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='PUBLIC')

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.CharField(max_length=300, default='text/plain') # it will be this temporarily
    # post = models.ForeignKey(Post, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'post'], name='unique_user_post_like')
        ]

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    commentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='text/markdown')
    dateCreated = models.DateTimeField(auto_now_add=True)