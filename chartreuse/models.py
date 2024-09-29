from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    displayName = models.CharField(max_length=100)
    host = models.URLField()
    github = models.URLField()
    profileImage = models.URLField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    date_created  = models.DateTimeField(auto_now_add=True)