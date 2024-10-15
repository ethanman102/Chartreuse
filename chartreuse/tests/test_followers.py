from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from urllib.parse import quote
from .. import models

class FollowersTestCases(TestCase):
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

        # Create test users
        self.client.post(reverse('chartreuse:user-list'), self.test_user_1_data, format='json')
        self.client.post(reverse('chartreuse:user-list'), self.test_user_2_data, format='json')

    
    def test_follow_user(self):
        '''
        This tests adding a follower.
        '''
        # Log in as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        user_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # Greg (user 1) is followed by John (user 2)
        response = self.client.post(reverse('chartreuse:add_follower', args=[user_id, follower_id]))

        # Check if follower added successfully
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'Follower added')

    
    def test_unfollow_user(self):
        '''
        This tests removing a follower.
        '''
        # Log in as user 1 and a follower user 2 first
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        user_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        self.client.post(reverse('chartreuse:add_follower', args=[user_id, follower_id]))

        # Now remove user2 as a follower
        response = self.client.delete(reverse('chartreuse:remove_follower', args=[user_id, follower_id]))

        # Check if follower removed successfully
        self.assertEqual(response.status_code, 204)


    def test_get_followers(self):
        '''
        This tests getting followers for a user.
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        user_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # Greg (user 1) is followed by John (user 2)
        self.client.post(reverse('chartreuse:add_follower', args=[user_id, follower_id]))

        # Get the list of followers for Greg (user 1)
        response = self.client.get(reverse('chartreuse:get_followers', args=[user_id]))

        # Successfully got followers
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['followers'], list)
        self.assertEqual(len(response.json()['followers']), 1)  # Greg is followed by John

    
    def test_is_follower(self):
        '''
        This tests checking if a user is a follower.
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        user_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # Greg (user 1) is followed by John (user 2)
        self.client.post(reverse('chartreuse:add_follower', args=[user_id, follower_id]))

        # Check if John is following Greg
        response = self.client.get(reverse('chartreuse:is_follower', args=[user_id, follower_id]))  # Greg is author, John is foreign_author

        # Successfully verified follower status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Is a follower')
        
