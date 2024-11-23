from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse
from urllib.parse import quote
import json
from ..views import Host
from ..models import User,Node
import base64
from django.contrib.auth.models import User as AuthUser

class UserTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = APIClient()

        # set the hostname
        cls.hostname = 'http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/'
        Host.host = cls.hostname

        # Test user data
        cls.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
            'username': 'greg',
            'password': 'ABC123!!!',
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        cls.test_user_2_data = {
            'displayName': 'John Smith',
            'github': 'http://github.com/jiori',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'john',
            'password': '87@398dh817b!',
            'firstName': 'John',
            'lastName': 'Smith',
        }

        cls.test_user_3_data = {
            'displayName': 'Benjamin Stanley',
            'github': 'http://github.com/bstanley',
            'profileImage': 'https://i.imgur.com/abcd.jpeg',
            'username': 'benjamin',
            'password': 'fwef!&123',
            'firstName': 'Benjamin',
            'lastName': 'Stanley',
        }

        cls.node = Node.objects.create(host='http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',username='abc',password='123',follow_status='INCOMING',status='ENABLED')
        cls.creds = {'Authorization' : 'Basic ' + base64.b64encode(b'abc:123').decode('utf-8')}

        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json',headers=cls.creds)
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_2_data, format='json',headers=cls.creds)
        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_3_data, format='json',headers=cls.creds)
        

        

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()

    def test_create_user(self):
        '''
        This tests creating a user.

        '''


        response = self.client.post(reverse('chartreuse:user-list'), {
            'displayName': 'Jane Doe',
            'github': 'http://github.com/jdoe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'jane',
            'password': 'ABC123!!!',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, format='json',headers=self.creds)

        # Successfully created user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['type'], 'author')
        self.assertEqual(response.json()['id'], f'{self.hostname}api/authors/4')
        self.assertEqual(response.json()['host'], self.hostname)
        self.assertEqual(response.json()['displayName'], 'Jane Doe')
        self.assertEqual(response.json()['github'], 'http://github.com/jdoe')
        self.assertEqual(response.json()['profileImage'], 'https://i.imgur.com/1234.jpeg')
        self.assertEqual(response.json()['page'], f"{self.hostname}/authors/{response.json()['id']}")
    
    def test_get_all_users(self):
        '''
        This tests getting all users from the database.
        '''
        response = self.client.get(reverse('chartreuse:user-list'),headers=self.creds)

        # Successfully got all users
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["authors"]), 3)

        # Check if the users are correct
        self.assertEqual(response.json()["authors"][0]['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()["authors"][1]['displayName'], 'John Smith')
        self.assertEqual(response.json()["authors"][2]['displayName'], 'Benjamin Stanley')
    
    def test_create_user_invalid_password(self):
        '''
        This tests creating a user with an invalid password.
        '''
        response = self.client.post(reverse('chartreuse:user-list'), {
            'displayName': 'Jane Doe',
            'github': 'http://github.com/jdoe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'jane',
            'password': 'ABC',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, format='json',headers=self.creds)

        # Invalid password
        self.assertEqual(response.status_code, 400)

    def test_get_user(self):
        '''
        This tests getting a specific user.
        '''
        user_id = quote(f"{self.hostname}api/authors/1", safe='')
        response = self.client.get(reverse('chartreuse:user-detail', args=[user_id]),headers=self.creds)

        # Successfully got user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['github'], 'http://github.com/gjohnson')
        self.assertEqual(response.json()['profileImage'], 'https://i.imgur.com/k7XVwpB.jpeg')
        self.assertEqual(response.json()['type'], 'author')
        self.assertEqual(response.json()['page'], f"{self.hostname}/authors/{response.json()['id']}")
        self.assertEqual(response.json()['id'], f'{self.hostname}api/authors/1')
        self.assertEqual(response.json()['host'], self.hostname)
        
    def test_get_user_invalid_id(self):
        '''
        This tests getting a user with an invalid id.
        '''
        user_id = quote(f"{self.hostname}api/authors/100", safe='')
        response = self.client.get(reverse('chartreuse:user-detail', args=[user_id]),headers=self.creds)

        # User does not exist
        self.assertEqual(response.status_code, 404)
    
    def test_delete_user(self):
        '''
        This tests deleting a user.
        '''
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })
        self.assertEqual(response.status_code, 200)

        greg = AuthUser.objects.get(username='greg')
        self.client.force_login(greg)
        print(self.client.session['_auth_user_id'],'hiii')
   

        user_id = quote(f"{self.hostname}api/authors/1", safe='')
        response = self.client.delete(reverse('chartreuse:user-detail', args=[user_id]),headers=self.creds)

        # Successfully deleted user
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], 'User deleted successfully.')
    
    def test_delete_user_invalid_id(self):
        '''
        This tests deleting a user with an invalid id.
        '''
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        user_id = quote(f"{self.hostname}api/authors/100", safe='')
        response = self.client.delete(reverse('chartreuse:user-detail', args=[user_id]),headers=self.creds)

        # User does not exist
        self.assertEqual(response.status_code, 404)
    
    def test_update_user(self):
        '''
        This tests updating a user.
        '''
        user_id = quote(f"{self.hostname}api/authors/1", safe='')
        url = reverse('chartreuse:user-detail', args=[user_id])

        data = {
            "github": "http://github.com/newgithub",
            "profileImage": "https://i.imgur.com/1234.jpeg",
            }
        
        # login as user 1
        self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        },headers=self.creds)

        response = self.client.put(url, data=json.dumps(data), content_type='application/json',headers=self.creds)
    
        # Successfully updated user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['github'], 'http://github.com/newgithub')
        self.assertEqual(response.json()['profileImage'], 'https://i.imgur.com/1234.jpeg')
    
    def test_login_success(self):
        """
        Test that a valid user can log in successfully
        """
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": "User logged in successfully."})
    
    def test_login_missing_password(self):
        """
        Test that login fails when password is missing
        """
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'testuser'
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Username and password are required."})

    def test_login_missing_username(self):
        """
        Test that login fails when username is missing
        """
        response = self.client.post(reverse('chartreuse:login_user'), {
            'password': 'password'
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Username and password are required."})

    def test_login_invalid_credentials(self):
        """
        Test that login fails when invalid credentials are provided
        """
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'invaliduser',
            'password': 'password'
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid credentials."})
    
