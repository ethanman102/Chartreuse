from django.test import TestCase, Client
from django.urls import reverse
from urllib.parse import quote
from rest_framework.test import APIClient
from .. import models

class FriendsTestCases(TestCase):
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


    def test_get_friends(self):
        '''
        This tests getting friends for a user.
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        author_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # Greg (user 1) is followed by John (user 2) and vice versa
        self.client.post(reverse('chartreuse:add_follower', args=[author_id, follower_id]))  # Greg followed by John
        self.client.post(reverse('chartreuse:add_follower', args=[follower_id, author_id]))  # John followed by Greg

        # Get the list of friends for Greg (user 1)
        response = self.client.get(reverse('chartreuse:get_friends', args=[author_id]))

        # Successfully got friends
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['friends'], list)
        self.assertEqual(len(response.json()['friends']), 1)  # Greg and John are friends

    
    def test_check_friendship(self):
        '''
        This tests checking if two users are friends (mutual followers).
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        author_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # Greg (user 1) follows John (user 2) and John follows Greg
        self.client.post(reverse('chartreuse:add_follower', args=[author_id, follower_id]))  # Greg followed by John
        self.client.post(reverse('chartreuse:add_follower', args=[follower_id, author_id]))  # John followed by Greg

        # Check if Greg and John are friends (mutual followers)
        response = self.client.get(reverse('chartreuse:check_friendship', args=[author_id, follower_id]))

        # Successfully verified friendship status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Authors are friends')
        
        # Check when they are not friends (one-sided follow)
        self.client.delete(reverse('chartreuse:remove_follower', args=[author_id, follower_id]))  # Greg unfollowed by John

        response = self.client.get(reverse('chartreuse:check_friendship', args=[author_id, follower_id]))
        
        # Should return that they are not friends
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'Authors are not friends')