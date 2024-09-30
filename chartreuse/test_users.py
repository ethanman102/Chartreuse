from django.test import TestCase, Client
from django.urls import reverse
import json

class UserTestCases(TestCase):
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

        self.test_user_3_data = {
            'displayName': 'Benjamin Stanley',
            'github': 'http://github.com/bstanley',
            'profileImage': 'https://i.imgur.com/abcd.jpeg',
            'username': 'benjamin',
            'password': 'fwef!&123',
            'host': 'http://nodeaaaa/api/',
            'firstName': 'Benjamin',
            'lastName': 'Stanley',
        }

        self.client.post(reverse('chartreuse:create_user'), self.test_user_1_data, format='json')
        self.client.post(reverse('chartreuse:create_user'), self.test_user_2_data, format='json')
        self.client.post(reverse('chartreuse:create_user'), self.test_user_3_data, format='json')
    
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
            'host': 'http://nodeaaaa/api/',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, format='json')

        # Successfully created user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['displayName'], 'Jane Doe')
        self.assertEqual(response.json()['github'], 'http://github.com/jdoe')
        self.assertEqual(response.json()['profileImage'], 'https://i.imgur.com/1234.jpeg')
        self.assertEqual(response.json()['type'], 'author')
        self.assertEqual(response.json()['page'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/api/authors/jane")
        self.assertEqual(response.json()['id'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/api/authors/4')
        self.assertEqual(response.json()['host'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/api/')
    
    def test_get_all_users(self):
        '''
        This tests getting all users from the database.
        '''
        response = self.client.get(reverse('chartreuse:get_users'))

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
        response = self.client.post(reverse('chartreuse:create_user'), {
            'displayName': 'Jane Doe',
            'github': 'http://github.com/jdoe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'jane',
            'password': 'ABC',
            'host': 'http://nodeaaaa/api/',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, format='json')

        # Invalid password
        self.assertEqual(response.status_code, 400)

    def test_get_user(self):
        '''
        This tests getting a specific user.
        '''
        response = self.client.get(reverse('chartreuse:user', args=[1]))

        # Successfully got user
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['displayName'], 'Greg Johnson')
        self.assertEqual(response.json()['github'], 'http://github.com/gjohnson')
        self.assertEqual(response.json()['profileImage'], 'https://i.imgur.com/k7XVwpB.jpeg')
        self.assertEqual(response.json()['type'], 'author')
        self.assertEqual(response.json()['page'], "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/api/authors/greg")
        self.assertEqual(response.json()['id'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/api/authors/1')
        self.assertEqual(response.json()['host'], 'https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/api/')
        
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
        # login as user 1
        response = self.client.post(reverse('chartreuse:login_user'), {
            'username': 'greg',
            'password': 'ABC123!!!'
        })

        response = self.client.delete(reverse('chartreuse:user', args=[1]))

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
        url = reverse('chartreuse:user', args=[1])

        data = {
            "github": "http://github.com/newgithub",
            "profileImage": "https://i.imgur.com/1234.jpeg",
            }

        response = self.client.put(url, json.dumps(data))
    
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
