from django.test import TestCase, Client
from django.urls import reverse
from urllib.parse import quote
from .. import models

class GithubTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()

        # Test user data
        cls.test_user_1_data = {
            'displayName': 'Julia',
            'github': 'http://github.com/Julia-Dantas',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'julia',
            'password': 'ABC123!!!',
            'host': 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',
            'firstName': 'Julia',
            'lastName': 'Dantas',
        }

        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json')
        cls.user_id = quote(f"{cls.test_user_1_data['host']}authors/1", safe='')

    
    def test_get_events(self):
        '''
        This tests getting a users git events.
        '''
        response = self.client.get(reverse('chartreuse:get_events', args=[self.user_id]))
    
        # Successfully got response
        self.assertEqual(response.status_code, 200)
    
    def test_get_starred(self):
        '''
        This tests getting a users starred repos.
        '''
        response = self.client.get(reverse('chartreuse:get_starred', args=[self.user_id]))

        # Successfully got response
        self.assertEqual(response.status_code, 200)
    
    def test_get_subscriptions(self):
        '''
        This tests getting a users watched repos.
        '''
        response = self.client.get(reverse('chartreuse:get_subscriptions', args=[self.user_id]))

        # Successfully got response
        self.assertEqual(response.status_code, 200)