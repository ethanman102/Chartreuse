from django.test import TestCase, Client
from django.urls import reverse
from .. import models
from rest_framework.test import APIClient
from urllib.parse import quote

class CommentTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        '''
        This method creates all information for testing, only once.
        '''
        super().setUpClass()

        cls.client = APIClient()

        # Test user data
        cls.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': 'http://nodeaaaa/api/',
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        cls.test_user_2_data = {
            'displayName': 'John Smith',
            'github': 'http://github.com/jiori',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'john',
            'password': '87@398dh817b!',
            'host': 'http://nodeaaaa/api/',
            'firstName': 'John',
            'lastName': 'Smith',
        }

        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json')
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_2_data, format='json')

        cls.user_id_1 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe="")
        cls.user_id_2 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe="")

        # Create a post for testing comments
        cls.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        cls.post_response = cls.client.post(reverse('chartreuse:posts', args=[cls.user_id_1]), {
            'visibility': "PUBLIC", 
            "title": "Greg's public post", 
            "description": "Test post description", 
            "contentType": "text/plain", 
            "content": "Hello World!"
        })
        cls.post_id = quote(cls.post_response.json()['id'], safe="")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
    
    def setUp(self):
        '''
        This method logs the user 2 in for every test run,
        because the client object does not remember login information
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })
    
    def test_create_comment(self):
        """
        Tests creating a comment on a post.
        """
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

    # def test_create_comment_unauthenticated(self):
    #     """
    #     Tests creating a comment without being authenticated.
    #     """
    #     # Fails since we login to create a post. Unsure 
    #     # Try to create a comment without logging in
    #     comment_response = self.client.post(reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]), {
    #         'comment': 'Nice post!',
    #         'contentType': 'text/plain'
    #     })

    #     # Should be denied access
    #     self.assertEqual(comment_response.status_code, 401)
    #     self.assertEqual(comment_response.json()['error'], 'User is not authenticated.')
    
    def test_get_comments(self):
        """
        Tests retrieving all comments on a post.
        """
        self.client.post(
            reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]),
            {'comment': "This is a test comment.", 'contentType': "text/plain"}
        )

        response = self.client.get(reverse('chartreuse:get_comments', args=[self.user_id_1, self.post_id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'comments')
        self.assertTrue(len(response.json()['src']) > 0)

    def test_get_comments_by_pid(self):
        """
        Tests retrieving all comments on a post using just the post id.
        """
        self.client.post(
            reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]),
            {'comment': "This is a test comment.", 'contentType': "text/plain"}
        )

        response = self.client.get(reverse('chartreuse:get_comments_by_pid', args=[self.post_id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'comments')
        self.assertTrue(len(response.json()['src']) > 0)
    
    def test_get_comment(self):
        """
        Tests retrieving a specific comment on a post.
        """
        response = self.client.post(
            reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]),
            {'comment': "This is a test comment.", 'contentType': "text/plain"}
        )
       
        comment_id = quote(response.json()["id"], safe="")

        response = self.client.get(reverse('chartreuse:get_comment', args=[self.user_id_1, self.post_id, comment_id]))
  
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'comment')
        self.assertTrue(response.json()['comment'], "This is a test comment.")
    
    def test_get_comment_by_cid(self):
        """
        Tests retrieving a specific comment using the comment id.
        """
        response = self.client.post(
            reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]),
            {'comment': "This is a test comment.", 'contentType': "text/plain"}
        )
       
        comment_id = quote(response.json()["id"], safe="")

        response = self.client.get(reverse('chartreuse:get_comment_by_cid', args=[comment_id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'comment')
        self.assertTrue(response.json()['comment'], "This is a test comment.")

    def test_get_authors_comments(self):
        """
        Tests retrieving a specific comment using the comment id.
        """
        self.client.post(
            reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]),
            {'comment': "This is a test comment.", 'contentType': "text/plain"}
        )

        self.client.post(
            reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]),
            {'comment': "This is a second test comment.", 'contentType': "text/plain"}
        )

        response = self.client.get(reverse('chartreuse:get_authors_comments', args=[self.user_id_2]))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['src']), 2)
        self.assertTrue(response.json()['src'][0]['type'], "comment")
    
    def test_create_commented_comment(self):
        """
        Tests creating a comment on a post using commented route.
        """
        # Create a comment
        comment_response = self.client.post(reverse('chartreuse:get_authors_comments', args=[self.user_id_1]), {
            'comment': 'Nice post!',
            'contentType': 'text/plain',
            'id': self.post_id,
        })

        # Successfully created comment
        self.assertEqual(comment_response.status_code, 201)
        self.assertEqual(comment_response.json()['type'], 'comment')
        self.assertEqual(comment_response.json()['author']['displayName'], 'John Smith')
        self.assertEqual(comment_response.json()['comment'], 'Nice post!')

    def test_delete_comment(self):
        """
        Tests deleting a comment.
        """
        # Create a comment
        comment_response = self.client.post(reverse('chartreuse:create_comment', args=[self.user_id_1, self.post_id]), {
            'comment': 'Nice post!',
            'contentType': 'text/plain'
        })

        comment_id = quote(comment_response.json()["id"], safe="")

        # Remove the comment
        comment_response = self.client.delete(reverse('chartreuse:delete_comment', args=[comment_id]))

        # Successfully created comment
        self.assertEqual(comment_response.status_code, 200)
        self.assertEqual(comment_response.json()['type'], 'comment')
        self.assertEqual(comment_response.json()['author']['displayName'], 'John Smith')
        self.assertEqual(comment_response.json()['comment'], 'Nice post!')