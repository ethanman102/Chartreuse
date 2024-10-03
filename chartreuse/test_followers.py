from django.test import TestCase, Client
from django.urls import reverse
from . import models

class FollowersTestCases(TestCase):
    def setUp(self):
        self.client = Client()

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

        # Create test users
        self.client.post(reverse('chartreuse:create_user'), self.test_user_1_data, format='json')
        self.client.post(reverse('chartreuse:create_user'), self.test_user_2_data, format='json')

    
    def test_follow_user(self):
        '''
        This tests adding a follower.
        '''
        # Log in as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        # Greg (user 1) follows John (user 2)
        response = self.client.post(reverse('chartreuse:add_follower', args=[1, 2]))

        # Check if follower added successfully
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['message'], 'Follower added')

    
    def test_unfollow_user(self):
        '''
        This tests removing a follower.
        '''
        # Log in as user 1 and follow user 2 first
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        self.client.post(reverse('chartreuse:add_follower', args=[1, 2]))

        # Now unfollow user 2
        response = self.client.delete(reverse('chartreuse:remove_follower', args=[1, 2]))

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

        # Greg (user 1) follows John (user 2)
        self.client.post(reverse('chartreuse:add_follower', args=[1, 2]))

        # Get the list of followers for John (user 2)
        response = self.client.get(reverse('chartreuse:get_followers', args=[2]))

        # Successfully got followers
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['followers'], list)
        self.assertEqual(len(response.json()['followers']), 1)  # Greg is following John

    
    def test_is_follower(self):
        '''
        This tests checking if a user is a follower.
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        # Greg (user 1) follows John (user 2)
        self.client.post(reverse('chartreuse:add_follower', args=[1, 2]))

        # Check if Greg is following John
        response = self.client.get(reverse('chartreuse:is_follower', args=[2, 1]))  # John is author, Greg is foreign_author

        # Successfully verified follower status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Is a follower')
        

