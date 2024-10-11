from django.test import TestCase, Client
from django.urls import reverse
from . import models
from rest_framework.test import APIClient

class LikeTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Test user data
        self.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': 'http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        self.test_user_2_data = {
            'displayName': 'John Smith',
            'github': 'http://github.com/jiori',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'john',
            'password': '87@398dh817b!',
            'host': 'http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',
            'firstName': 'John',
            'lastName': 'Smith',
        }

        self.test_user_3_data = {
            'displayName': 'Benjamin Stanley',
            'github': 'http://github.com/bstanley',
            'profileImage': 'https://i.imgur.com/abcd.jpeg',
            'username': 'benjamin',
            'password': 'fwef!&123',
            'host': 'http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',
            'firstName': 'Benjamin',
            'lastName': 'Stanley',
        }

        self.client.post(reverse('chartreuse:user-list'), self.test_user_1_data, format='json')
        self.client.post(reverse('chartreuse:user-list'), self.test_user_2_data, format='json')
        self.client.post(reverse('chartreuse:user-list'), self.test_user_3_data, format='json')

        models.Like.objects.create(user=models.User.objects.get(url_id="https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1"), post='http://nodebbbb/authors/222/posts/249')
        models.Like.objects.create(user=models.User.objects.get(url_id="https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1"), post='http://nodebbbb/authors/223/posts/1')
        models.Like.objects.create(user=models.User.objects.get(url_id="https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2"), post='http://nodebbbb/authors/222/posts/249')
        models.Like.objects.create(user=models.User.objects.get(url_id="https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/3"), post='http://nodebbbb/authors/222/posts/249')
    
    def test_like_post(self):
        '''
        This tests liking a post.
        '''
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        response = self.client.post(reverse('chartreuse:like', args=["https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1"]), {'post': "http://nodebbbb/authors/3/posts/230"})

        # Successfully liked post
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'like')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/5")
        self.assertEqual(response.json()['object'], "http://nodebbbb/authors/3/posts/230")
    
    def test_like_post_twice_invalid(self):
        '''
        This tests liking a post twice.
        '''
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        response = self.client.post(reverse('chartreuse:like', args=["https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1"]), {
            'post': "http://nodebbbb/authors/222/posts/2"
        })

        response = self.client.post(reverse('chartreuse:like', args=["https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1"]), {
            'post': "http://nodebbbb/authors/222/posts/2"
        })

        # Cannot like post twice
        self.assertEqual(response.status_code, 400)
    
    def test_get_like(self):
        """
        This tests getting a like by an author.
        """
        # Assuming you have a user and like objects created in your test setup
        response = self.client.get(reverse('chartreuse:get_like_object', args=["https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", 1]))

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'like')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/1")
        self.assertEqual(response.json()['object'], "http://nodebbbb/authors/222/posts/249")
    
    def test_get_all_likes_by_author(self):
        '''
        This tests getting all likes by an author.
        '''
        response = self.client.get(reverse('chartreuse:get_liked', args=["https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1"]))

        # Successfully got all likes
        self.assertEqual(response.status_code, 200)

        # Assert the values in the response
        self.assertEqual(response.json()['page'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/posts/')
        self.assertEqual(response.json()['page_number'], 1)
        self.assertEqual(response.json()['size'], 50)
        self.assertEqual(response.json()['count'], 2)

        # Assert that 'src' is a list
        self.assertIsInstance(response.json()['src'], list)
        self.assertEqual(len(response.json()['src']), 2) # there are 2 likes by author 1

        # Assert the structure of the first like in 'src'
        like_object = response.json()['src'][0]
        self.assertEqual(like_object['id'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/1')
        self.assertEqual(like_object['object'], 'http://nodebbbb/authors/222/posts/249')

        like_object_2 = response.json()['src'][1]
        self.assertEqual(like_object_2['id'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/2')
        self.assertEqual(like_object_2['object'], 'http://nodebbbb/authors/223/posts/1')