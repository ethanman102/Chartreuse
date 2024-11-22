from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from urllib.parse import quote
from ..models import User, Node
from chartreuse.views import Host
import base64

class PostTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = APIClient()

        Host.host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

        cls.host = Host.host

        cls.client = APIClient()

        # Test user data
        cls.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': cls.host,
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        cls.test_user_2_data = {
            'displayName': 'John Smith',
            'github': 'http://github.com/jiori',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'john',
            'password': '87@398dh817b!',
            'host': cls.host,
            'firstName': 'John',
            'lastName': 'Smith',
        }

        cls.test_user_3_data = {
            'displayName': 'Benjamin Stanley',
            'github': 'http://github.com/bstanley',
            'profileImage': 'https://i.imgur.com/abcd.jpeg',
            'username': 'benjamin',
            'password': 'fwef!&123',
            'host': cls.host,
            'firstName': 'Benjamin',
            'lastName': 'Stanley',
        }
        cls.node = Node.objects.create(host='http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',username='abc',password='123',follow_status='INCOMING',status='ENABLED')
        cls.creds = {'Authorization' : 'Basic ' + base64.b64encode(b'abc:123').decode('utf-8')}

        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json', headers=cls.creds)
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_2_data, format='json', headers=cls.creds)
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_3_data, format='json',headers=cls.creds)

        cls.user_id_1 = quote(f"{cls.host}chartreuse/api/authors/1", safe = "")
        cls.user_id_2 = quote(f"{cls.host}chartreuse/api/authors/2", safe = "")
        cls.user_id_3 = quote(f"{cls.host}chartreuse/api/authors/3", safe = "")

        # log in as user 1 and make a post
        cls.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        cls.response = cls.client.post(reverse('chartreuse:posts', args=[cls.user_id_1]), {
            'visibility': "PUBLIC", 
            "title": "Gregs public post", 
            "description": "Test post description", 
            "contentType": "text/plain", 
            "content": "Hello World! \nThis is a short message from greg!"
        }, headers=cls.creds)

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()

    def test_creating_post(self):
        """
        This tests creating a post.
        """
        # Successfully created post
        self.assertEqual(self.response.status_code, 201)
        self.assertEqual(self.response.json()['type'], 'post')
        self.assertEqual(self.response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(self.response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1/posts/1")
        self.assertEqual(self.response.json()['visibility'], 'PUBLIC')
        self.assertEqual(self.response.json()['title'], 'Gregs public post')
        self.assertEqual(self.response.json()['description'], 'Test post description')
        self.assertEqual(self.response.json()['contentType'], 'text/plain')
        self.assertEqual(self.response.json()['content'], 'Hello World! \nThis is a short message from greg!')

    # def test_creating_post_unauthenticated(self):
    #     """
    #     This tests creating a post from an unathenticated user.
    #     """
    #     # Need to sign out
    #     # send post request 
    #     response = self.client.post(reverse('chartreuse:posts', args=[self.user_id_1]), {
    #         'visibility': "PUBLIC", 
    #         "title": "Gregs public post", 
    #         "description": "Test post description", 
    #         "contentType": "text/plain", 
    #         "content": "Hello World! \nThis is a short message from greg!"
    #     })

    #     # We should be denied access
    #     self.assertEqual(response.status_code, 401)
    #     self.assertEqual(response.json()["error"], "User is not authenticated.")
        
    def test_get_post(self):
        """
        Tests getting a post.
        """
        # Assuming you have a user and post objects created in the test setup
        response = self.client.get(reverse('chartreuse:post', args=[self.user_id_1, quote(self.response.json()['id'], safe="")]), headers=self.creds)

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'post')

    def test_get_posts_by_author(self):
        """
        Tests getting posts by an author.
        """
        # Assuming you have a user and post objects created in the test setup
        response = self.client.get(reverse('chartreuse:posts', args=[self.user_id_1]), headers=self.creds)

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'posts')

    def test_delete_post(self):
        """
        Tests deleting a post.
        """
        response = self.client.delete(reverse('chartreuse:post', args=[self.user_id_1, quote(self.response.json()['id'], safe="")]), headers=self.creds)
 
        # Successfully removed post
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'post')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1/posts/1")
        self.assertEqual(response.json()['visibility'], 'DELETED')

    def test_update_post(self):
        """
        Tests updating a post.
        """
        # we create a new client here because for some reason the header for PUT request
        # is messed up when APIClient is put into setUpClass
        client = APIClient()

        host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

        user_id_1 = quote(f"{host}chartreuse/api/authors/1", safe = "")

        # log in as user 1 and edit a post
        response = client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        response = client.put(reverse('chartreuse:post', args=[user_id_1, quote(self.response.json()['id'], safe="")]), {
            'visibility': "PUBLIC", 
            "title": "Gregs updated public post", 
            "description": "New test post description", 
            "contentType": "text/plain", 
            "content": "New content"
        }, headers=self.creds)

        # Successfully updated post
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'post')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/chartreuse/api/authors/1/posts/1")
        self.assertEqual(response.json()['visibility'], 'PUBLIC')
        self.assertEqual(response.json()['title'], 'Gregs updated public post')
        self.assertEqual(response.json()['description'], 'New test post description')
        self.assertEqual(response.json()['contentType'], 'text/plain')
        self.assertEqual(response.json()['content'], 'New content')