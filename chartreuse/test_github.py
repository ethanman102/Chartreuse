from django.test import TestCase, Client
from django.urls import reverse

class LikeTestCases(TestCase):
    def setUp(self):
        self.client = Client()

        # Test user data
        self.test_user_1_data = {
            'displayName': 'Julia',
            'github': 'http://github.com/Julia-Dantas',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'julia',
            'password': 'ABC123!!!',
            'host': 'http://nodeaaaa/api/',
            'firstName': 'Julia',
            'lastName': 'Dantas',
        }

        self.client.post(reverse('chartreuse:create_user'), self.test_user_1_data, format='json')
    
    def test_get_events(self):
        '''
        This tests getting a users git events.
        '''
        response = self.client.get(reverse('chartreuse:get_events', args=[1]))

        # Successfully got response
        self.assertEqual(response.status_code, 200)
    
    def test_get_starred(self):
        '''
        This tests getting a users starred repos.
        '''
        response = self.client.get(reverse('chartreuse:get_starred', args=[1]))

        # Successfully got response
        self.assertEqual(response.status_code, 200)
    
    def test_get_subscriptions(self):
        '''
        This tests getting a users watched repos.
        '''
        response = self.client.get(reverse('chartreuse:get_subscriptions', args=[1]))

        # Successfully got response
        self.assertEqual(response.status_code, 200)