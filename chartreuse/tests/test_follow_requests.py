from django.test import TestCase, Client
from django.urls import reverse
from ..models import User, FollowRequest, Follow
from django.shortcuts import get_object_or_404
from urllib.parse import quote
from rest_framework.test import APIClient

class FollowRequestsTestCases(TestCase):
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

    
    def test_send_follow_request(self):
        '''
        This tests sending a follow request to another user.
        '''
        # Log in as user 1
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        author_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # Send follow request to user 2
        response = self.client.post(reverse('chartreuse:send_follow_request', args=[author_id]))

        # Successfully sent follow request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Follow request sent.')

    
    def test_approve_follow_request(self):
        '''
        This tests approving a follow request.
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })
        author_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # User 1 sends a follow request
        self.client.post(reverse('chartreuse:send_follow_request', args=[author_id]))

        # Log out user to switch context
        self.client.logout()

        # Log back in as user 2 (who will approve the request)
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        greg = get_object_or_404(User, url_id="https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1")
        john = get_object_or_404(User, url_id="https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2")

        # Approve the follow request as user 2
        follow_request = FollowRequest.objects.get(requester=john, requestee=greg)
        response = self.client.post(reverse('chartreuse:accept_follow_request', args=[follow_request.id]))

        # Successfully approved follow request
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Follow request accepted.')
        self.assertEqual(Follow.objects.count(), 1)

    def test_reject_follow_request(self):
        '''
        This tests rejecting a follow request.
        '''
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        author_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # User 1 sends a follow request
        self.client.post(reverse('chartreuse:send_follow_request', args=[author_id]))

        # Log out user to switch context
        self.client.logout()

        # Log back in as user 2 (who will reject the request)
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'john',
            'password': '87@398dh817b!'
        })

        current_user = get_object_or_404(User, url_id="https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2")
        author = get_object_or_404(User, url_id="https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1")

        # Reject the follow request as user 2
        follow_request = FollowRequest.objects.get(requester=current_user, requestee=author)
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

        author_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
        follower_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/2", safe='')

        # User 1 sends a follow request
        self.client.post(reverse('chartreuse:send_follow_request', args=[author_id]))

        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        response = self.client.get(reverse('chartreuse:get_follow_requests'))

        # Successfully got follow requests
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()['follow_requests'], list)
        self.assertEqual(len(response.json()['follow_requests']), 1)  # Greg has a follow request