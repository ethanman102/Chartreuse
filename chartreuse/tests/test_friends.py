from django.test import TestCase
from django.urls import reverse
from urllib.parse import quote
from rest_framework.test import APIClient
from chartreuse.views import Host

class FriendsTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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

        # Create test users
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json')
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_2_data, format='json')

        # Log in as user 1
        cls.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        # 2 users add each other to the Follows table
        cls.author_id = quote(f"{cls.test_user_1_data['host']}authors/1", safe='')
        cls.follower_id = quote(f"{cls.test_user_2_data['host']}authors/2", safe='')

        # Greg (user 1) is followed by John (user 2) and vice versa
        cls.client.post(reverse('chartreuse:add_follower', args=[cls.author_id, cls.follower_id]))  # Greg followed by John
        cls.client.post(reverse('chartreuse:add_follower', args=[cls.follower_id, cls.author_id]))  # John followed by Greg

    def setUp(self):
        '''
        Log in as user 1 again because setUpClass does not carry login information
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()

    def test_get_friends(self):
        '''
        This tests getting friends for a user.
        '''
        # Get the list of friends for Greg (user 1)
        response = self.client.get(reverse('chartreuse:get_friends', args=[self.author_id]))

        # Successfully got friends
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['friends'], list)
        self.assertEqual(len(response.json()['friends']), 1)  # Greg and John are friends

    
    def test_check_friendship(self):
        '''
        This tests checking if two users are friends (mutual followers).
        '''
        # Check if Greg and John are friends (mutual followers)
        response = self.client.get(reverse('chartreuse:check_friendship', args=[self.author_id, self.follower_id]))

        # Successfully verified friendship status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Authors are friends')
        
        # Check when they are not friends (one-sided follow)
        self.client.delete(reverse('chartreuse:remove_follower', args=[self.author_id, self.follower_id]))  # Greg unfollowed by John

        response = self.client.get(reverse('chartreuse:check_friendship', args=[self.author_id, self.follower_id]))
        
        # Should return that they are not friends
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'Authors are not friends')