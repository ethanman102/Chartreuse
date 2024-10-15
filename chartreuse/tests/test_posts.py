from django.test import TestCase, Client
from django.urls import reverse
from .. import models
from rest_framework.test import APIClient
from urllib.parse import quote

class PostTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Test user data
        self.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': 'http://nodeaaaa/api/',
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        self.test_user_2_data = {
            'displayName': 'John Smith',
            'github': 'http://github.com/jiori',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'john',
            'password': '87@398dh817b!',
            'host': 'http://nodeaaaa/api/',
            'firstName': 'John',
            'lastName': 'Smith',
        }

        self.test_user_3_data = {
            'displayName': 'Benjamin Stanley',
            'github': 'http://github.com/bstanley',
            'profileImage': 'https://i.imgur.com/abcd.jpeg',
            'username': 'benjamin',
            'password': 'fwef!&123',
            'host': 'http://nodeaaaa/api/',
            'firstName': 'Benjamin',
            'lastName': 'Stanley',
        }

        self.client.post(reverse('chartreuse:user-list'), self.test_user_1_data, format='json')
        self.client.post(reverse('chartreuse:user-list'), self.test_user_2_data, format='json')
        self.client.post(reverse('chartreuse:user-list'), self.test_user_3_data, format='json')

        self.user_id_1 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe = "")
        self.user_id_2 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe = "")
        self.user_id_3 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/3", safe = "")

    def test_creating_post(self):
        """
        This tests creating a post.
        """
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        response = self.client.post(reverse('chartreuse:posts', args=[self.user_id_1]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        # Successfully created post
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['type'], 'post')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/posts/1")
        self.assertEqual(response.json()['visibility'], 'PUBLIC')
        self.assertEqual(response.json()['title'], 'Gregs public post')
        self.assertEqual(response.json()['description'], 'Test post description')
        self.assertEqual(response.json()['contentType'], 'text/plain')
        self.assertEqual(response.json()['content'], 'Hello World! \nThis is a short message from greg!')

    def test_creating_post_unauthenticated(self):
        """
        This tests creating a post from an unathenticated user.
        """
        # Purposely do not log in
        # send post request 
        response = self.client.post(reverse('chartreuse:posts', args=[self.user_id_1]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        # We should be denied access
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "User is not authenticated.")
        
    def test_get_post(self):
        """
        Tests getting a post.
        """
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        post = self.client.post(reverse('chartreuse:posts', args=[self.user_id_1]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        # Assuming you have a user and post objects created in the test setup
        response = self.client.get(reverse('chartreuse:post', args=[self.user_id_1, quote(post.json()['id'], safe="")]))

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'post')

    def test_get_posts_by_author(self):
        """
        Tests getting posts by an author.
        """# login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        self.client.post(reverse('chartreuse:posts', args=[self.user_id_1]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        # Assuming you have a user and post objects created in the test setup
        response = self.client.get(reverse('chartreuse:posts', args=[self.user_id_1]))

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'posts')

    def test_delete_post(self):
        """
        Tests deleting a post.
        """
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        post = self.client.post(reverse('chartreuse:posts', args=[self.user_id_1]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        response = self.client.delete(reverse('chartreuse:post', args=[self.user_id_1, quote(post.json()['id'], safe="")]))
 
        # Successfully removed post
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'post')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/posts/1")
        self.assertEqual(response.json()['visibility'], 'DELETED')

    def test_update_post(self):
        """
        Tests updating a post.
        """
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        
        post = self.client.post(reverse('chartreuse:posts', args=[self.user_id_1]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        response = self.client.put(reverse('chartreuse:post', args=[self.user_id_1, quote(post.json()['id'], safe="")]), {
            'visibility': "PUBLIC", 
            "title": "Gregs updated public post", 
            "description": "New test post description", 
            "contentType": "text/plain", 
            "content": "New content"
            })

        # Successfully updated post
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'post')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/posts/1")
        self.assertEqual(response.json()['visibility'], 'PUBLIC')
        self.assertEqual(response.json()['title'], 'Gregs updated public post')
        self.assertEqual(response.json()['description'], 'New test post description')
        self.assertEqual(response.json()['contentType'], 'text/plain')
        self.assertEqual(response.json()['content'], 'New content')
        