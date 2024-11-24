from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from chartreuse.views import Host
from ..models import User, Node,Post,Comment
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
                "id": 'https://FQID/NEW',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'https://newest_author/2/2/2',
                    "page": 'fillerdata',
                    "host": 'https://newest_author/',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'fakeimg.png'
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

        author_queryset = User.objects.filter(url_id='https://newest_author/2/2/2')
        self.assertTrue(author_queryset.exists())
        self.assertEqual(author_queryset.count(),1)

        # check that the post was added.

        post_queryset = Post.objects.filter(url_id='https://FQID/NEW')
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
                "id": 'https://FQID/NEW',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'https://newest_author/2/2/2',
                    "page": 'fillerdata',
                    "host": 'https://newest_author/',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'fakeimg.png'
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

        author_queryset = User.objects.filter(url_id='https://newest_author/2/2/2')
        self.assertTrue(author_queryset.exists())
        self.assertEqual(author_queryset.count(),1)

        # check that the post was added.

        post_queryset = Post.objects.filter(url_id='https://FQID/NEW')
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
                "id": 'https://FQID/NEW',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'https://newest_author/2/2/2',
                    "page": 'fillerdata',
                    "host": 'https://newest_author/',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'fakeimg.png'
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
        post_queryset = Post.objects.filter(url_id='https://FQID/NEW')
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
                "id": 'https://FQID/NEW',
                "description": 'ETHAN DESCRIPTION',
                "contentType": 'text/plain',
                "content": 'This is ethans test post',
                "author": {
                    "type": "author",
                    "id": 'https://newest_author/2/2/2',
                    "page": 'fillerdata',
                    "host": 'https://newest_author/',
                    "displayName": 'ETHANAUTHOR',
                    "github": '',
                    "profileImage": 'fakeimg.png'
                },
                "comments":{
                    "type": "comments",
                    "src": [
                        {
                        "type": "comment",
                        "author": {
                            "type": "author",
                            "id": 'https://newest_author/2/a/3',
                            "page": 'whateverpage',
                            "host": 'https://woah',
                            "displayName": 'comment author',
                            "github": '',
                            "profileImage": 'testtest.png',
                        },
                        "comment": 'NEW COMMENT HI',
                        "contentType": 'text/plain',
                        "published": datetime.now(),
                        "id": 'http://newcomment/',
                        "post": 'https://FQID/NEW',
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

        author_queryset = User.objects.filter(url_id='https://newest_author/2/2/2')
        self.assertTrue(author_queryset.exists())
        self.assertEqual(author_queryset.count(),1)

        # check that the comment author got added
        author_queryset_comment = User.objects.filter(url_id='https://newest_author/2/a/3')
        self.assertTrue(author_queryset_comment.exists())
        self.assertEqual(author_queryset_comment.count(),1)

        # check that the post got added.
        post_queryset = Post.objects.filter(url_id='https://FQID/NEW')
        self.assertTrue(post_queryset.exists())
        self.assertEqual(post_queryset.count(),1)

        new_post = post_queryset[0]

        self.assertEqual(new_post.title,'ETHAN TITLE')
        self.assertEqual(new_post.content,'This is ethans test post')
        self.assertEqual(new_post.contentType,'text/plain')
        self.assertEqual(new_post.description,'ETHAN DESCRIPTION')
        self.assertEqual(new_post.user,author_queryset[0])

        # check that the comment got added.

        comment_queryset = Comment.objects.filter(url_id='http://newcomment/')

        self.assertTrue(comment_queryset.exists())
        self.assertEqual(comment_queryset.count(),1)
        comment = comment_queryset[0]

        self.assertEqual(comment.comment,'NEW COMMENT HI')
        self.assertEqual(comment.contentType,'text/plain')
        self.assertEqual(comment.user,author_queryset_comment[0])


    '''
    def test_new_post_with_likes(self):
        pass

    def test_new_post_like(self):
        pass

    def test_new_comment_like(self):
        pass

    def test_new_comment(self):
        pass
    '''
