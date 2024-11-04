from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from urllib.parse import quote

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

        self.user_id_1 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe = "")
        self.user_id_2 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe = "")
        self.user_id_3 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/3", safe = "")

    def test_like_post(self):
        '''
        This tests liking a post.
        '''
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })
    
        self.client.post(reverse('chartreuse:posts', args=[self.user_id_2]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        post_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1" , safe="")

        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        response = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': post_id})

        # Successfully liked post
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'like')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/1")
        self.assertEqual(response.json()['object'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1")
    
    def test_like_post_twice_invalid(self):
        '''
        This tests liking a post twice.
        '''
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        self.client.post(reverse('chartreuse:posts', args=[self.user_id_2]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        post_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1" , safe="")

        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        response = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {
            'post': post_id
        })

        response = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {
            'post': post_id
        })

        # Cannot like post twice
        self.assertEqual(response.status_code, 400)
    
    def test_get_like(self):
        """
        This tests getting a like by an author.
        """
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        self.client.post(reverse('chartreuse:posts', args=[self.user_id_2]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        post_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1" , safe="")

        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        like = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': post_id})

        like_id = like.json()['id']
        user_id = like.json()['author']['id']
        user_id = quote(user_id, safe='')
        like_id = quote(like_id, safe='')

        response = self.client.get(reverse('chartreuse:get_like_object', args=[user_id, like_id]))

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'like')
        self.assertEqual(response.json()['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/1")
        self.assertEqual(response.json()['object'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1")
    
    def test_get_all_likes_by_author(self):
        '''
        This tests getting all likes by an author.
        '''

        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        self.client.post(reverse('chartreuse:posts', args=[self.user_id_2]), {'visibility': "PUBLIC", "title": "Gregs 1st public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})
        self.client.post(reverse('chartreuse:posts', args=[self.user_id_2]), {'visibility': "PUBLIC", "title": "Gregs 2nd public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})
        post_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1" , safe="")
        post_id_2 = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/2" , safe="")

        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        like1 = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': post_id})
        like2 = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': post_id_2})

        user_id = like1.json()['author']['id']
        user_id = quote(user_id, safe='')
        
        response = self.client.get(reverse('chartreuse:get_liked', args=[user_id]))

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
        self.assertEqual(like_object['object'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1')

        like_object_2 = response.json()['src'][1]
        self.assertEqual(like_object_2['id'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/2')
        self.assertEqual(like_object_2['object'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/2')

    def test_get_post_likes(self):
        """
        This tests getting likes on a post.
        """
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        self.client.post(reverse('chartreuse:posts', args=[self.user_id_2]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        post_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1" , safe="")

        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        like = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': post_id})

        like_id = like.json()['id']
        user_id = like.json()['author']['id']
        user_id = quote(user_id, safe='')
        like_id = quote(like_id, safe='')
        response = self.client.get(reverse('chartreuse:post_likes', args=[user_id, post_id]))

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'likes')
        self.assertEqual(response.json()["src"][0]['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['src'][0]['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/1")
        self.assertEqual(response.json()["src"][0]['object'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1")



    def test_get_comment_likes(self):
        """
        This tests getting likes on a comment.
        """
        # Login as user 2
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        # Create a post
        self.client.post(reverse('chartreuse:posts', args=[self.user_id_2]), {'visibility': "PUBLIC", "title": "Gregs public post", "description": "Test post description", "contentType": "text/plain", "content": "Hello World! \nThis is a short message from greg!"})

        post_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1" , safe="")

        # Login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        # Comment on the post
        comment_response = self.client.post(reverse('chartreuse:create_comment', args=[self.user_id_2, post_id]), {
            'comment': 'Nice post!',
            'contentType': 'text/plain'
        })

        comment_id = quote(comment_response.json()["id"], safe="")

        # Like the comment
        like = self.client.post(reverse('chartreuse:like', args=[self.user_id_1]), {'post': post_id, "comment":comment_id})

        like_id = like.json()['id']
        user_id = like.json()['author']['id']
        user_id = quote(user_id, safe='')
        like_id = quote(like_id, safe='')

        # get the comment likes
        response = self.client.get(reverse('chartreuse:comment_likes', args=[user_id, post_id, comment_id]))

        # Assertions to verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'likes')
        self.assertEqual(response.json()["src"][0]['author']['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()["src"][0]['id'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1/liked/1")
        self.assertEqual(response.json()["src"][0]['object'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2/posts/1")