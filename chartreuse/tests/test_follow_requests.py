from django.test import TestCase
from django.urls import reverse
from ..models import User, FollowRequest, Follow
from django.shortcuts import get_object_or_404
from rest_framework.test import APIClient
from .. import views

class FollowRequestsTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        views.Host.host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

        cls.client = APIClient()

        # Test user data
        cls.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'https://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        cls.test_user_2_data = {
            'displayName': 'John Smith',
            'github': 'https://github.com/jiori',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'john',
            'password': '87@398dh817b!',
            'host': 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',
            'firstName': 'John',
            'lastName': 'Smith',
        }

        # Create test users
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json')
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_2_data, format='json')

        # log in as user 1
        cls.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        # sends a follow request to user 2
        cls.response = cls.client.post(reverse('chartreuse:send_follow_request', args=[f"{cls.test_user_2_data['host']}authors/2"]))

        # user 1 logout
        cls.client.logout()

        cls.greg = get_object_or_404(User, url_id=f"{cls.test_user_1_data['host']}authors/1")
        cls.john = get_object_or_404(User, url_id=f"{cls.test_user_2_data['host']}authors/2")
    
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
        response = self.client.post(reverse('chartreuse:accept_follow_request', args=[follow_request.id]))

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
        response = self.client.delete(reverse('chartreuse:reject_follow_request', args=[follow_request.id]))

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

        response = self.client.get(reverse('chartreuse:get_follow_requests'))

        # Successfully got follow requests
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['follow_requests'], list)
        self.assertEqual(len(response.json()['follow_requests']), 1)  # John has a follow request