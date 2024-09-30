from django.db import models
from django.contrib.auth.models import User as AuthUser

class User(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    displayName = models.CharField(max_length=100)
    host = models.URLField()
    github = models.URLField()
    profileImage = models.URLField()
    dateCreated  = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    title = models.CharField(max_length=200)
    id = models.URLField(primary_key=True)
    description = models.TextField()
    contentType = models.CharField(max_length=50, default='text/plain')
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.DateTimeField()
    visibility = models.CharField(max_length=20, default='PUBLIC')

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.CharField(max_length=300, default='text/plain')
    dateCreated = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    commentType = models.CharField(max_length=50, default='text/markdown')
    dateCreated = models.DateTimeField(auto_now_add=True)