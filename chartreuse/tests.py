from django.test import TestCase, Client
from django.urls import reverse
from .models import User
import json

class UserTestCases(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test user objects
        self.test_user_1 = User.objects.create(
            displayName='Greg Johnson',
            github='http://github.com/gjohnson',
            profileImage='https://i.imgur.com/k7XVwpB.jpeg',
            username='greg',
            password='ABC123!!!',
            host = 'http://nodeaaaa/api/'
        )

        self.test_user_2 = User.objects.create(
            displayName='John Smith',
            github='http://github.com/jiori',
            profileImage='https://i.imgur.com/1234.jpeg',
            username='greg',
            password='87@398dh817b!',
            host = 'http://nodeaaaa/api/'
        )

        self.test_user_3 = User.objects.create(
            displayName='Benjamin Stanley',
            github='http://github.com/bstanley',
            profileImage='https://i.imgur.com/abcd.jpeg',
            username='greg',
            password='fwef!&123',
            host = 'http://nodeaaaa/api/'
        )

    def test_get_all_users(self):
        '''
        This tests getting all users from the database.
        '''
        response = self.client.get(reverse('chartreuse:get_users'))

        # Successfully got all users
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

        # Check if the users are correct
        self.assertEqual(response.json()[0]['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()[1]['displayName'], 'John Smith')
        self.assertEqual(response.json()[2]['displayName'], 'Benjamin Stanley')
    
    def test_create_user(self):
        '''
        This tests creating a user.
        '''
        response = self.client.post(reverse('chartreuse:create_user'), {
            'displayName': 'Jane Doe',
            'github': 'http://github.com/jdoe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'jane',
            'password': 'ABC123!!!',
            'host': 'http://nodeaaaa/api/'
        }, format='json')

        # Successfully created user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['displayName'], 'Jane Doe')
    
    def test_create_user_invalid_password(self):
        '''
        This tests creating a user with an invalid password.
        '''
        response = self.client.post(reverse('chartreuse:create_user'), {
            'displayName': 'Jane Doe',
            'github': 'http://github.com/jdoe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'jane',
            'password': 'ABC',
            'host': 'http://nodeaaaa/api/'
        }, format='json')

        # Invalid password
        self.assertEqual(response.status_code, 400)

    def test_get_user(self):
        '''
        This tests getting a specific user.
        '''
        response = self.client.get(reverse('chartreuse:user', args=[self.test_user_1.id]))

        # Successfully got user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['displayName'], 'Greg Johnson')
    
    def test_get_user_invalid_id(self):
        '''
        This tests getting a user with an invalid id.
        '''
        response = self.client.get(reverse('chartreuse:user', args=[100]))

        # User does not exist
        self.assertEqual(response.status_code, 404)
    
    def test_delete_user(self):
        '''
        This tests deleting a user.
        '''
        response = self.client.delete(reverse('chartreuse:user', args=[self.test_user_1.id]))

        # Successfully deleted user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'User deleted successfully.')
    
    def test_delete_user_invalid_id(self):
        '''
        This tests deleting a user with an invalid id.
        '''
        response = self.client.delete(reverse('chartreuse:user', args=[100]))

        # User does not exist
        self.assertEqual(response.status_code, 404)
    
    def test_update_user(self):
        '''
        This tests updating a user.
        '''
        url = reverse('chartreuse:user', args=[self.test_user_1.id])

        data = {
            "github": "http://github.com/newgithub",
            "profileImage": "https://i.imgur.com/1234.jpeg",
            }

        response = self.client.put(url, json.dumps(data))
    
        # Successfully updated user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['github'], 'http://github.com/newgithub')
        self.assertEqual(response.json()['profileImage'], 'https://i.imgur.com/1234.jpeg')
    
    def test_update_password(self):
        '''
        This tests updating a user's password.
        '''
        url = reverse('chartreuse:change_password', args=[self.test_user_1.id])

        data = {
            "password": "qoiwhrioq7!@"
            }

        response = self.client.put(url, json.dumps(data))
    
        # Successfully updated password
        self.assertEqual(response.status_code, 200)
    
    def test_update_invalid_password(self):
        '''
        This tests updating a user's password with an invalid password.
        '''
        url = reverse('chartreuse:change_password', args=[self.test_user_1.id])

        data = {
            "password": "abc"
            }

        response = self.client.put(url, json.dumps(data))
    
        # Invalid password
        self.assertEqual(response.status_code, 400)