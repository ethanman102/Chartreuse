from django.test import TestCase, Client
from django.urls import reverse
from .. import models
from rest_framework.test import APIClient
from urllib.parse import quote

class CommentTestCases(TestCase):
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

        self.client.post(reverse('chartreuse:user-list'), self.test_user_1_data, format='json')
        self.client.post(reverse('chartreuse:user-list'), self.test_user_2_data, format='json')

        self.user_id_1 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe="")
        self.user_id_2 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe="")

        # Create a post for testing comments
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        self.post_response = self.client.post(reverse('chartreuse:posts', args=[self.user_id_1]), {
            'visibility': "PUBLIC", 
            "title": "Greg's public post", 
            "description": "Test post description", 
            "contentType": "text/plain", 
            "content": "Hello World!"
        })
        self.post_id = quote(self.post_response.json()['id'], safe="")

    def test_create_comment(self):
        """
        Tests creating a comment on a post.
        """
        # login as user 2 (John Smith)
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        # Create a comment
        comment_response = self.client.post(reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]), {
            'comment': 'Nice post!',
            'contentType': 'text/plain'
        })

        # Successfully created comment
        self.assertEqual(comment_response.status_code, 201)
        self.assertEqual(comment_response.json()['type'], 'comment')
        self.assertEqual(comment_response.json()['author']['displayName'], 'John Smith')
        self.assertEqual(comment_response.json()['comment'], 'Nice post!')

    def test_create_comment_unauthenticated(self):
        """
        Tests creating a comment without being authenticated.
        """
        # Try to create a comment without logging in
        comment_response = self.client.post(reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]), {
            'comment': 'Nice post!',
            'contentType': 'text/plain'
        })

        # Should be denied access
        self.assertEqual(comment_response.status_code, 401)
        self.assertEqual(comment_response.json()['error'], 'User is not authenticated.')

    def test_get_comments(self):
        """
        Tests retrieving all comments on a post.
        """

        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        self.client.post(
            reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]),
            {'comment': "This is a test comment.", 'contentType': "text/plain"}
        )

        response = self.client.get(reverse('chartreuse:get_comments', args=[self.user_id_1, self.post_id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'comments')
        self.assertTrue(len(response.json()['comments']) > 0)

    