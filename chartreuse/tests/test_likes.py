from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from urllib.parse import quote
from chartreuse.views import Host
from ..models import User

class LikeTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        print("In LikeTestCases", User.objects.all())

        cls.client = APIClient()

        Host.host = 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/'

        cls.host = Host.host

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

        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json')
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_2_data, format='json')
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_3_data, format='json')

        cls.user_id_1 = quote(f"{cls.host}authors/1", safe = "")
        cls.user_id_2 = quote(f"{cls.host}authors/2", safe = "")
        cls.user_id_3 = quote(f"{cls.host}authors/3", safe = "")

        # log in as john and create 2 posts
        cls.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        # first post
        cls.client.post(reverse('chartreuse:posts', args=[cls.user_id_2]), {
            'visibility': "PUBLIC", 
            "title": "Gregs public post", 
            "description": "Test post description", 
            "contentType": "text/plain", 
            "content": "Hello World! \nThis is a short message from greg!"
        })
        cls.post_id = quote(f"{cls.host}authors/2/posts/1" , safe="")

        # second post
        cls.client.post(reverse('chartreuse:posts', args=[cls.user_id_2]), {
            'visibility': "PUBLIC", 
            "title": "Gregs 2nd public post", 
            "description": "Test post description", 
            "contentType": "text/plain", 
            "content": "Hello World! \nThis is a short message from greg!"
        })
        cls.post_id_2 = quote(f"{cls.host}authors/2/posts/2" , safe="")

    def setUp(self):
        '''
        Log in as user 1 because setUpClass does not keep log in information
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()

    def test_like_post(self):
        '''
        This tests liking a post.
        '''
        response = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': self.post_id})

        # Successfully liked post
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'like')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], f"{self.host}authors/1/liked/1")
        self.assertEqual(response.json()['object'], f"{self.host}authors/2/posts/1")
    
    def test_like_post_twice_invalid(self):
        '''
        This tests liking a post twice.
        '''
        response = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {
            'post': self.post_id
        })

        response = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {
            'post': self.post_id
        })

        # Cannot like post twice
        self.assertEqual(response.status_code, 400)
    
    def test_get_like(self):
        """
        This tests getting a like by an author.
        """
        like = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': self.post_id})

        like_id = like.json()['id']
        user_id = like.json()['author']['id']
        user_id = quote(user_id, safe='')
        like_id = quote(like_id, safe='')

        response = self.client.get(reverse('chartreuse:get_like_object', args=[user_id, like_id]))

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'like')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], f"{self.host}authors/1/liked/1")
        self.assertEqual(response.json()['object'], f"{self.host}authors/2/posts/1")
    
    def test_get_all_likes_by_author(self):
        '''
        This tests getting all likes by an author.
        '''
        like1 = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': self.post_id})
        like2 = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': self.post_id_2})

        user_id = like1.json()['author']['id']
        user_id = quote(user_id, safe='')
        
        response = self.client.get(reverse('chartreuse:get_liked', args=[user_id]))

        # Successfully got all likes
        self.assertEqual(response.status_code, 200)

        # Assert the values in the response
        self.assertEqual(response.json()['page'], f'{self.host}authors/1/posts/')
        self.assertEqual(response.json()['page_number'], 1)
        self.assertEqual(response.json()['size'], 50)
        self.assertEqual(response.json()['count'], 2)

        # Assert that 'src' is a list
        self.assertIsInstance(response.json()['src'], list)
        self.assertEqual(len(response.json()['src']), 2) # there are 2 likes by author 1

        # Assert the structure of the first like in 'src'
        like_object = response.json()['src'][0]
        self.assertEqual(like_object['id'], f'{self.host}authors/1/liked/1')
        self.assertEqual(like_object['object'], f'{self.host}authors/2/posts/1')

        like_object_2 = response.json()['src'][1]
        self.assertEqual(like_object_2['id'], f'{self.host}authors/1/liked/2')
        self.assertEqual(like_object_2['object'], f'{self.host}authors/2/posts/2')

    def test_get_post_likes(self):
        """
        This tests getting likes on a post.
        """
        like = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': self.post_id})

        like_id = like.json()['id']
        user_id = like.json()['author']['id']
        user_id = quote(user_id, safe='')
        like_id = quote(like_id, safe='')

        # Missing 1 required argument: 'request'
        response = self.client.get(reverse('chartreuse:post_likes', args=[user_id, self.post_id]))

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'likes')
        self.assertEqual(response.json()["src"][0]['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['src'][0]['id'], f"{self.host}authors/1/liked/1")
        self.assertEqual(response.json()["src"][0]['object'], f"{self.host}authors/2/posts/1")

    def test_get_comment_likes(self):
        """
        This tests getting likes on a comment.
        """
        # Comment on the post
        comment_response = self.client.post(reverse('chartreuse:create_comment', args=[self.user_id_2, self.post_id]), {
            'comment': 'Nice post!',
            'contentType': 'text/plain'
        })

        comment_id = quote(comment_response.json()["id"], safe="")

        # Like the comment
        like = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': self.post_id, "comment":comment_id})

        like_id = like.json()['id']
        user_id = like.json()['author']['id']
        user_id = quote(user_id, safe='')
        like_id = quote(like_id, safe='')

        # get the comment likes
        response = self.client.get(reverse('chartreuse:comment_likes', args=[user_id, self.post_id, comment_id]))  

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'likes')
        self.assertEqual(response.json()["src"][0]['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()["src"][0]['id'], f"{self.host}authors/1/liked/1")
        self.assertEqual(response.json()["src"][0]['object'], f"{self.host}authors/1/commented/1")

        