from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.db.models import UniqueConstraint

VISIBILITY_CHOICES = {"PUBLIC": "PUBLIC", "FRIENDS": "FRIENDS", "UNLISTED": "UNLISTED", "DELETED": "DELETED"}
CONTENT_TYPE_CHOICES = {"text/commonmark": "text/commonmark", "text/plain": "text/plain", "application/base64": "application/base64", "image/png;base64": "image/png;base64", "image/jpeg;base64": "image/jpeg;base64"}

class User(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    url_id = models.URLField(primary_key=True)
    displayName = models.CharField(max_length=100)
    host = models.URLField()
    github = models.URLField()
    profileImage = models.URLField()
    dateCreated  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User(pk={self.pk}, username={self.user.username}, displayName={self.displayName}, host={self.host}, github={self.github}, profileImage={self.profileImage})"

class Post(models.Model):
    title = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)
    url_id = models.URLField()
    description = models.TextField()
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='text/plain')
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='PUBLIC')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.url_id = f"{self.user.url_id}/posts/{self.pk}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Post(id={self.id}, url_id={self.url_id}, title={self.title}, description={self.description}, contentType={self.contentType}, content={self.content}, user={self.user}, published={self.published}, visibility={self.visibility})"

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    url_id = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES, default='text/markdown')
    dateCreated = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.url_id = f"{self.user.url_id}/commented/{self.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment(id={self.id}, url_id={self.url_id}, contentType={self.contentType}, content={self.comment}, user={self.user}, published={self.dateCreated})"

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    url_id = models.URLField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.ForeignObject(Comment, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'post'], name='unique_user_post_like')
        ]
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.url_id = f"{self.user.url_id}/liked/{self.pk}"
    
    def __str__(self):
        return f"Like(id={self.id}, url_id={self.url_id}, user={self.user}, post={self.post}, dateCreated={self.dateCreated})"

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE) # Use user.following to get all the users that a user is following
    followed = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE) # Use user.followers to get all the users following that particular user
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')


class FollowRequest(models.Model):
    requester = models.ForeignKey(User, related_name="follow_requests_sent", on_delete=models.CASCADE)
    requestee = models.ForeignKey(User, related_name="follow_requests_received", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

class GithubPolling(models.Model):
    last_polled = models.DateTimeField(auto_now_add=True)