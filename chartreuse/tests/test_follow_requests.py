from django.test import TestCase
from django.urls import reverse
from ..models import User, FollowRequest, Follow, Node
from django.shortcuts import get_object_or_404
from rest_framework.test import APIClient
from chartreuse.views import Host
from urllib.parse import quote
import base64


import json

class FollowRequestsTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Host.host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

        cls.host = Host.host

        cls.client = APIClient()

        # Test user data
        cls.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'https://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': cls.host,
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        cls.test_user_2_data = {
            'displayName': 'John Smith',
            'github': 'https://github.com/jiori',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'john',
            'password': '87@398dh817b!',
            'host': cls.host,
            'firstName': 'John',
            'lastName': 'Smith',
        }
        cls.node = Node.objects.create(host='http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',username='abc',password='123',follow_status='INCOMING',status='ENABLED')
        cls.creds = {'Authorization' : 'Basic ' + base64.b64encode(b'abc:123').decode('utf-8')}

        # Create test users
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json', headers=cls.creds)
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_2_data, format='json', headers=cls.creds)

        # log in as user 1
        test_response = cls.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        # sends a follow request to user 2
        cls.response = cls.client.post(reverse('chartreuse:send_follow_request', args=[quote(f"{cls.test_user_2_data['host']}chartreuse/api/authors/2", safe='')]), headers=cls.creds)

        # user 1 logout
        cls.client.logout()

        cls.greg = get_object_or_404(User, url_id=f"{cls.test_user_1_data['host']}chartreuse/api/authors/1")
        cls.john = get_object_or_404(User, url_id=f"{cls.test_user_2_data['host']}chartreuse/api/authors/2")

    def setUp(self):
        '''
        Log in as user 1 because setUpClass does not keep log in information
        '''
        # log in as user 1
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()
    
    def test_send_follow_request(self):
        '''
        This tests sending a follow request to another user.
        '''
        # Successfully sent follow request
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.json()['message'], 'Follow request sent.')
    
    def test_approve_follow_request(self):
        '''
        This tests approving a follow request.
        '''
        # Log back in as user 2 (who will approve the request)
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        # Approve the follow request as user 2
        follow_request = FollowRequest.objects.get(requester=self.greg, requestee=self.john)
        response = self.client.post(reverse('chartreuse:accept_follow_request', args=[follow_request.id]), headers=self.creds)

        # Successfully approved follow request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Follow request accepted.')
        self.assertEqual(Follow.objects.count(), 1)

    def test_reject_follow_request(self):
        '''
        This tests rejecting a follow request.
        '''
        # Log back in as user 2 (who will reject the request)
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        # Reject the follow request as user 2
        follow_request = FollowRequest.objects.get(requester=self.greg, requestee=self.john)
        response = self.client.delete(reverse('chartreuse:reject_follow_request', args=[follow_request.id]), headers=self.creds)

        # Successfully rejected follow request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Follow request rejected.')
        self.assertEqual(FollowRequest.objects.count(), 0)

    def test_get_follow_requests(self):
        '''
        This tests getting follow requests for a user.
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        response = self.client.get(reverse('chartreuse:get_follow_requests'), headers=self.creds)

        # Successfully got follow requests
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['follow_requests'], list)
        self.assertEqual(len(response.json()['follow_requests']), 1)  # John has a follow request