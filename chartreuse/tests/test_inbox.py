from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from chartreuse.views import Host
from ..models import User, Node,Post,Comment,Like
import base64
import json
from django.contrib.auth.models import User as AuthUser
from datetime import datetime
from urllib.parse import quote

class AuthenticationTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Host.host = "http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

        cls.host = Host.host

        cls.client = APIClient()

        # create test node with the correct auth!!
        cls.node = Node.objects.create(host='http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',username='abc',password='123',follow_status='INCOMING',status='ENABLED')
        cls.creds = {'Authorization' : 'Basic ' + base64.b64encode(b'abc:123').decode('utf-8')}

        # Test user data
        cls.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json',headers=cls.creds)

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()
    

    
    def test_author_not_existing(self):
        
        response = self.client.post(reverse('chartreuse:inbox',args=[100000]), {
            'displayName': 'Jane Doe',
            'github': 'http://github.com/jdoe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'jane',
            'password': 'ABC123!!!',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, content_type='application/json',headers=self.creds)

        self.assertEqual(response.status_code,404)

        data = json.loads(response.content)
        self.assertNotEqual(data.get('error'),None)
        self.assertEqual(data.get('error'),'Author,100000,not found')

    
    def test_new_post(self):
        postObject = {
                "type": "post",
                "title": 'ETHAN TITLE',
                "id": 'http://github.com/gjohnson/id',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'http://github.com/gjohnson',
                    "page": 'fillerdata',
                    "host": 'http://github.com/gjohnson/2',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'https://profile.png'
                },
                "comments":{
                    "type": "comments",
                    "src": []
                },
                "likes": {
                    "types": "likes",
                    "src": []
                },
                "published": datetime.now(),
                "visibility": 'PUBLIC',
            }
        
        
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), postObject, content_type='application/json',headers=self.creds)

        self.assertEqual(response.status_code,200)
        
        data = json.loads(response.content)

        self.assertNotEqual(data.get('status'),None)
        self.assertEqual(data.get('status'),"Post added successfully")

        # check that the new author was added.

        author_queryset = User.objects.filter(url_id='http://github.com/gjohnson')
        self.assertTrue(author_queryset.exists())
        self.assertEqual(author_queryset.count(),1)

        # check that the post was added.

        post_queryset = Post.objects.filter(url_id='http://github.com/gjohnson/id')
        self.assertTrue(post_queryset.exists())
        self.assertEqual(post_queryset.count(),1)

        new_post = post_queryset[0]

        self.assertEqual(new_post.title,'ETHAN TITLE')
        self.assertEqual(new_post.content,'This is ethans test post')
        self.assertEqual(new_post.contentType,'text/plain')
        self.assertEqual(new_post.description,'ETHAN DESCRIPTION')
        self.assertEqual(new_post.user,author_queryset[0])

        
    def test_update_post(self):  
        postObject = {
                "type": "post",
                "title": 'ETHAN TITLE',
                "id": 'http://github.com/gjohnson/id',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'http://github.com/gjohnson',
                    "page": 'fillerdata',
                    "host": 'http://github.com/gjohnson/host',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'https://profile.png'
                },
                "comments":{
                    "type": "comments",
                    "src": []
                },
                "likes": {
                    "types": "likes",
                    "src": []
                },
                "published": datetime.now(),
                "visibility": 'PUBLIC',
            }
        
        
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), postObject, content_type='application/json',headers=self.creds)

        self.assertEqual(response.status_code,200)
        
        data = json.loads(response.content)

        self.assertNotEqual(data.get('status'),None)
        self.assertEqual(data.get('status'),"Post added successfully")

        # check that the new author was added.

        author_queryset = User.objects.filter(url_id='http://github.com/gjohnson')
        self.assertTrue(author_queryset.exists())
        self.assertEqual(author_queryset.count(),1)

        # check that the post was added.

        post_queryset = Post.objects.filter(url_id='http://github.com/gjohnson/id')
        self.assertTrue(post_queryset.exists())
        self.assertEqual(post_queryset.count(),1)

        new_post = post_queryset[0]

        self.assertEqual(new_post.title,'ETHAN TITLE')
        self.assertEqual(new_post.content,'This is ethans test post')
        self.assertEqual(new_post.contentType,'text/plain')
        self.assertEqual(new_post.description,'ETHAN DESCRIPTION')
        self.assertEqual(new_post.user,author_queryset[0])

        postObject = {
                "type": "post",
                "title": 'ETHAN TITLE NEWWWWWWWW',
                "id": 'http://github.com/gjohnson/id',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'http://github.com/gjohnson',
                    "page": 'fillerdata',
                    "host": 'http://github.com/gjohnson/host',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'https://profile.png'
                },
                "comments":{
                    "type": "comments",
                    "src": []
                },
                "likes": {
                    "types": "likes",
                    "src": []
                },
                "published": datetime.now(),
                "visibility": 'PUBLIC',
            }
        
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), postObject, content_type='application/json',headers=self.creds)
        post_queryset = Post.objects.filter(url_id='http://github.com/gjohnson/id')
        self.assertTrue(post_queryset.exists())
        self.assertEqual(post_queryset.count(),1)

        new_post = post_queryset[0]

        self.assertEqual(new_post.title,'ETHAN TITLE NEWWWWWWWW')
        self.assertEqual(new_post.content,'This is ethans test post')
        self.assertEqual(new_post.contentType,'text/plain')
        self.assertEqual(new_post.description,'ETHAN DESCRIPTION')
        self.assertEqual(new_post.user,author_queryset[0])

    
    def test_new_post_with_comments(self):
        postObject = {
                "type": "post",
                "title": 'ETHAN TITLE',
                "id": 'http://github.com/gjohnson/id',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'http://github.com/gjohnson',
                    "page": 'fillerdata',
                    "host": 'http://github.com/gjohnson/host',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'https://profile.png'
                },
                "comments":{
                    "type": "comments",
                    "src": [
                        {
                        "type": "comment",
                        "author": {
                            "type": "author",
                            "id": 'http://github.com/gjohnson/321',
                            "page": 'whateverpage',
                            "host": 'http://github.com/gjohnson/commentauthor',
                            "displayName": 'comment author',
                            "github": '',
                            "profileImage": 'https://profile.png',
                        },
                        "comment": 'NEW COMMENT HI',
                        "contentType": 'text/plain',
                        "published": datetime.now(),
                        "id": 'http://github.com/gjohnson/comment',
                        "post": 'http://github.com/gjohnson/id',
                    }
                    ]
                },
                "likes": {
                    "types": "likes",
                    "src": []
                },
                "published": datetime.now(),
                "visibility": 'PUBLIC',
            }
       
        
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), postObject, content_type='application/json',headers=self.creds)

        self.assertEqual(response.status_code,200)
        
        data = json.loads(response.content)

        self.assertNotEqual(data.get('status'),None)
        self.assertEqual(data.get('status'),"Post added successfully")

        # check that the new author was added.

        author_queryset = User.objects.filter(url_id='http://github.com/gjohnson')
        self.assertTrue(author_queryset.exists())
        self.assertEqual(author_queryset.count(),1)

        # check that the comment author got added
        author_queryset_comment = User.objects.filter(url_id='http://github.com/gjohnson/321')
        self.assertTrue(author_queryset_comment.exists())
        self.assertEqual(author_queryset_comment.count(),1)

        # check that the post got added.
        post_queryset = Post.objects.filter(url_id='http://github.com/gjohnson/id')
        self.assertTrue(post_queryset.exists())
        self.assertEqual(post_queryset.count(),1)

        new_post = post_queryset[0]

        self.assertEqual(new_post.title,'ETHAN TITLE')
        self.assertEqual(new_post.content,'This is ethans test post')
        self.assertEqual(new_post.contentType,'text/plain')
        self.assertEqual(new_post.description,'ETHAN DESCRIPTION')
        self.assertEqual(new_post.user,author_queryset[0])

        # check that the comment got added.

        comment_queryset = Comment.objects.filter(url_id='http://github.com/gjohnson/comment')

        self.assertTrue(comment_queryset.exists())
        self.assertEqual(comment_queryset.count(),1)
        comment = comment_queryset[0]

        self.assertEqual(comment.comment,'NEW COMMENT HI')
        self.assertEqual(comment.contentType,'text/plain')
        self.assertEqual(comment.user,author_queryset_comment[0])


    
    def test_new_post_with_likes(self):
        postObject = {
                "type": "post",
                "title": 'ETHAN TITLE',
                "id": 'http://github.com/gjohnson/id',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'http://github.com/gjohnson',
                    "page": 'fillerdata',
                    "host": 'http://github.com/gjohnson/host',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'https://profile.png'
                },
                "comments":{
                    "type": "comments",
                    "src": []
                },
                "likes": {
                    "types": "likes",
                    "src": [
                        {
                            "type": "like",
                            "author": {
                                "type": "author",
                                "id": 'http://github.com/gjohnson/likeauthor',
                                "page": 'whateverpage',
                                "host": 'http://github.com/gjohnson/woah',
                                "displayName": 'ETHANLIKE',
                                "github": '',
                                "profileImage": 'https://profile.png',
                            },
                            "published": datetime.now(),
                            "id": 'http://github.com/gjohnson/like',
                            "object": 'http://github.com/gjohnson/id'
                        }
                    ]
                },
                "published": datetime.now(),
                "visibility": 'PUBLIC',
            }
        
        
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), postObject, content_type='application/json',headers=self.creds)
        # check that items got added.
        self.assertEqual(response.status_code,200)
        
        data = json.loads(response.content)

        self.assertNotEqual(data.get('status'),None)
        self.assertEqual(data.get('status'),"Post added successfully")

        # check that the new author was added.

        author_queryset = User.objects.filter(url_id='http://github.com/gjohnson')
        self.assertTrue(author_queryset.exists())
        self.assertEqual(author_queryset.count(),1)

        # check that the post was added.

        post_queryset = Post.objects.filter(url_id='http://github.com/gjohnson/id')
        self.assertTrue(post_queryset.exists())
        self.assertEqual(post_queryset.count(),1)

        new_post = post_queryset[0]

        self.assertEqual(new_post.title,'ETHAN TITLE')
        self.assertEqual(new_post.content,'This is ethans test post')
        self.assertEqual(new_post.contentType,'text/plain')
        self.assertEqual(new_post.description,'ETHAN DESCRIPTION')
        self.assertEqual(new_post.user,author_queryset[0])

        # check like and like author got added
        author_queryset_like = User.objects.filter(url_id='http://github.com/gjohnson/likeauthor')
        self.assertTrue(author_queryset_like.exists())
        self.assertEqual(author_queryset_like.count(),1)

        # check that the like got added

        like_queryset = Like.objects.filter(url_id='http://github.com/gjohnson/like')
        self.assertTrue(like_queryset.exists())
        self.assertEqual(like_queryset.count(),1)

        like = like_queryset[0]
        self.assertEqual(like.user,author_queryset_like[0])

    def test_new_post_like(self):
        postObject = {
                "type": "post",
                "title": 'ETHAN TITLE',
                "id": 'http://github.com/gjohnson/id',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'http://github.com/gjohnson',
                    "page": 'fillerdata',
                    "host": 'http://github.com/gjohnson/host',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'https://profile.png'
                },
                "comments":{
                    "type": "comments",
                    "src": []
                },
                "likes": {
                    "types": "likes",
                    "src": [
                    ]
                },
                "published": datetime.now(),
                "visibility": 'PUBLIC',
            }
        
        
        self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), postObject, content_type='application/json',headers=self.creds)

        like_object = {
            "type": "like",
            "author": {
                "type": "author",
                "id": 'http://github.com/gjohnson/like',
                "page": 'whateverpage',
                "host": 'http://github.com/gjohnson/host',
                "displayName": 'ETHANLIKE',
                "github": '',
                "profileImage": 'https://profile.png',
            },
            "published": datetime.now(),
            "id": 'http://github.com/gjohnson/likeid',
            "object": 'http://github.com/gjohnson/id'
        }
        self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), like_object, content_type='application/json',headers=self.creds)

        # check that the like author got added
        author_queryset_like = User.objects.filter(url_id='http://github.com/gjohnson/like')
        self.assertTrue(author_queryset_like.exists())
        self.assertEqual(author_queryset_like.count(),1)

        # check that the like got added

        like_queryset = Like.objects.filter(url_id='http://github.com/gjohnson/likeid')
        self.assertTrue(like_queryset.exists())
        self.assertEqual(like_queryset.count(),1)

        like = like_queryset[0]
        self.assertEqual(like.user,author_queryset_like[0])


    def test_new_comment(self):
        postObject = {
                "type": "post",
                "title": 'ETHAN TITLE',
                "id": 'http://github.com/gjohnson/id',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'http://github.com/gjohnson',
                    "page": 'fillerdata',
                    "host": 'http://github.com/gjohnson/host',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'https://profile.png'
                },
                "comments":{
                    "type": "comments",
                    "src": []
                },
                "likes": {
                    "types": "likes",
                    "src": []
                },
                "published": datetime.now(),
                "visibility": 'PUBLIC',
            }
        
        
        self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), postObject, content_type='application/json',headers=self.creds)

        comment_obj = {
                        "type": "comment",
                        "author": {
                            "type": "author",
                            "id": 'http://github.com/gjohnson/commentauthor',
                            "page": 'whateverpage',
                            "host": 'http://github.com/gjohnson/host',
                            "displayName": 'comment author',
                            "github": '',
                            "profileImage": 'https://testtest.png',
                        },
                        "comment": 'NEW COMMENT HI',
                        "contentType": 'text/plain',
                        "published": datetime.now(),
                        "id": 'http://github.com/gjohnson/idcomment',
                        "post": 'http://github.com/gjohnson/id',
                    }
        
        self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), comment_obj, content_type='application/json',headers=self.creds)
        
        author_queryset_comment = User.objects.filter(url_id='http://github.com/gjohnson/commentauthor')
        self.assertTrue(author_queryset_comment.exists())
        self.assertEqual(author_queryset_comment.count(),1)
        
        comment_queryset = Comment.objects.filter(url_id='http://github.com/gjohnson/idcomment')

        self.assertTrue(comment_queryset.exists())
        self.assertEqual(comment_queryset.count(),1)
        comment = comment_queryset[0]

        self.assertEqual(comment.comment,'NEW COMMENT HI')
        self.assertEqual(comment.contentType,'text/plain')
        self.assertEqual(comment.user,author_queryset_comment[0])
    
    def test_new_post_invalid_author(self):
        postObject = {
                "type": "post",
                "title": 'ETHAN TITLE',
                "id": 'http://github.com/gjohnson/id',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'newest_author/2/2/2',
                    "page": 'fillerdata',
                    "host": '  https://host/',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'https://profile.png'
                },
                "comments":{
                    "type": "comments",
                    "src": []
                },
                "likes": {
                    "types": "likes",
                    "src": []
                },
                "published": datetime.now(),
                "visibility": 'PUBLIC',
            }
        
        
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), postObject, content_type='application/json',headers=self.creds)
        self.assertEqual(response.status_code,400)

    def test_like_no_object(self):
        
        like_object = {
            "type": "like",
            "author": {
                "type": "author",
                "id": 'http://github.com/gjohnson/like',
                "page": 'whateverpage',
                "host": 'http://github.com/gjohnson/host',
                "displayName": 'ETHANLIKE',
                "github": '',
                "profileImage": 'https://profile.png',
            },
            "published": datetime.now(),
            "id": 'http://github.com/gjohnson/likeid',
            "object": 'http://github.com/gjohnson/id'
        }
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), like_object, content_type='application/json',headers=self.creds)
        self.assertEqual(response.status_code,404)

    def test_invalid_like_keys(self):
        like_object = {
            "type": "like",
            "authoewr": {
                "type": "author",
                "id": 'http://github.com/gjohnson/like',
                "page": 'whateverpage',
                "host": 'http://github.com/gjohnson/host',
                "displayName": 'ETHANLIKE',
                "github": '',
                "profileImage": 'https://profile.png',
            },
            "publisewhed": datetime.now(),
            "ide": 'http://github.com/gjohnson/likeid',
            "object": 'http://github.com/gjohnson/id'
        }
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), like_object, content_type='application/json',headers=self.creds)
        self.assertEqual(response.status_code,400)

    def test_no_type_specified(self):
        
        like_object = {
            "author": {
                "type": "author",
                "id": 'http://github.com/gjohnson/like',
                "page": 'whateverpage',
                "host": 'http://github.com/gjohnson/host',
                "displayName": 'ETHANLIKE',
                "github": '',
                "profileImage": 'https://profile.png',
            },
            "published": datetime.now(),
            "id": 'http://github.com/gjohnson/likeid',
            "object": 'http://github.com/gjohnson/id'
        }
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), like_object, content_type='application/json',headers=self.creds)
        self.assertEqual(response.status_code,400)

    def test_comment_no_post(self):

        comment_obj = {
                        "type": "comment",
                        "author": {
                            "type": "author",
                            "id": 'http://github.com/gjohnson/commentauthor',
                            "page": 'whateverpage',
                            "host": 'http://github.com/gjohnson/host',
                            "displayName": 'comment author',
                            "github": '',
                            "profileImage": 'https://testtest.png',
                        },
                        "comment": 'NEW COMMENT HI',
                        "contentType": 'text/plain',
                        "published": datetime.now(),
                        "id": 'http://github.com/gjohnson/idcomment',
                        "post": 'http://github.com/gjohnson/id',
                    }
        
        response = self.client.post(reverse('chartreuse:inbox',args=[quote('http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1',safe='')]), comment_obj, content_type='application/json',headers=self.creds)
        self.assertEqual(response.status_code,404)


    




  
