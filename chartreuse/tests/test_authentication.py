from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from chartreuse.views import Host
from ..models import User, Node
import base64
from ..views import checkIfRequestAuthenticated
from requests import Request
import json
from django.contrib.auth.models import User as AuthUser

class AuthenticationTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Host.host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

        cls.host = Host.host

        cls.client = APIClient()

        # create test node with the correct auth!!
        cls.node = Node.objects.create(host='http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',username='abc',password='123',follow_status='INCOMING',status='ENABLED')
        cls.creds = {'Authorization' : 'Basic ' + base64.b64encode(b'abc:123').decode('utf-8')}




    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()
    
    def test_successful_incoming_authentication(self):
        # https://stackoverflow.com/questions/18869074/create-url-without-request-execution
        # Stack overflow post: Create url without request execution
        # Purpose: How to create a python requests object without actually making a request to a url.
        # Answered by: Lukasa on September 18, 2013 (Use requests.Request then .prepare())
        request = Request(url='https://None',auth=('abc','123')).prepare()
        response = checkIfRequestAuthenticated(request)
       
        self.assertEqual(response.status_code,200)
        self.assertNotEqual(response.status_code,401)

        data = json.loads(response.content)

        self.assertNotEqual(data.get('success'),None)
        self.assertEqual(data.get('error'),None)
    
    def test_wrong_username_authentication(self):
        request = Request(url='https://None',auth=('abcd','123')).prepare()
        response = checkIfRequestAuthenticated(request)
       
        self.assertEqual(response.status_code,401)
        self.assertNotEqual(response.status_code,200)

        data = json.loads(response.content)

        self.assertNotEqual(data.get('error'),None)
        self.assertEqual(data.get('success'),None)

    def test_wrong_password_authentication(self):
        request = Request(url='https://None',auth=('abc','1234')).prepare()
        response = checkIfRequestAuthenticated(request)
       
        self.assertEqual(response.status_code,401)
        self.assertNotEqual(response.status_code,200)

        data = json.loads(response.content)

        self.assertNotEqual(data.get('error'),None)
        self.assertEqual(data.get('success'),None)
    
    def test_disabled_node_authentication_rejection(self):
        Node.objects.create(host='http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',username='ZYX',password='432',follow_status='INCOMING',status='DISABLED')
        request = Request(url='https://None',auth=('ZYX','432')).prepare()
        response = checkIfRequestAuthenticated(request)

        self.assertEqual(response.status_code,401)
        self.assertNotEqual(response.status_code,200)

        data = json.loads(response.content)

        self.assertNotEqual(data.get('error'),None)
        self.assertEqual(data.get('success'),None)

    def test_successful_authentication_required_endpoint(self):
        response = self.client.post(reverse('chartreuse:user-list'), {
            'displayName': 'Jane Doe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'ethankk',
            'password': 'ABC123!!',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, format='json',headers=self.creds)

        self.assertEqual(response.status_code,200)
        self.assertNotEqual(response.status_code,401)

        data = json.loads(response.content)

        self.assertEqual(data.get('error'),None)

        self.assertNotEqual(data.get('type'),None)
        self.assertEqual(data.get('type'),'author')

        user_queryset = AuthUser.objects.filter(username='ethankk')
        
        self.assertEqual(user_queryset.exists(),True)
        self.assertEqual(user_queryset.count(),1)

        user = user_queryset[0]

        author_queryset = User.objects.filter(user=user)

        self.assertEqual(author_queryset.exists(),True)
        self.assertEqual(author_queryset.count(),1)

        author = author_queryset[0]

        self.assertEqual(author.displayName, 'Jane Doe')
        self.assertEqual(author.profileImage,'https://i.imgur.com/1234.jpeg')

    def test_api_authorization_incorrect_credentials_password(self):
        incorrect_password = {'Authorization' : 'Basic ' + base64.b64encode(b'abc:123222222').decode('utf-8')}
        response = self.client.post(reverse('chartreuse:user-list'), {
            'displayName': 'Jane Doe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'ethankk',
            'password': 'ABC123!!',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, format='json',headers=incorrect_password)

        self.assertEqual(response.status_code,401)

        data = json.loads(response.content)
        self.assertNotEqual(data.get('error'),None)

        user_queryset = AuthUser.objects.filter(username='ethankk')
        self.assertFalse(user_queryset.exists())

    def test_api_authorization_incorrect_credentials_username(self):
        incorrect_username = {'Authorization' : 'Basic ' + base64.b64encode(b'abcFEDFEF:123').decode('utf-8')}
        response = self.client.post(reverse('chartreuse:user-list'), {
            'displayName': 'Jane Doe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'ethankk',
            'password': 'ABC123!!',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, format='json',headers=incorrect_username)

        self.assertEqual(response.status_code,401)

        data = json.loads(response.content)
        self.assertNotEqual(data.get('error'),None)

        user_queryset = AuthUser.objects.filter(username='ethankk')
        self.assertFalse(user_queryset.exists())

    def test_api_authorization_disabled_node(self):
        Node.objects.create(host='http://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/',username='ZYX',password='432',follow_status='INCOMING',status='DISABLED')
        cred_of_disabled = {'Authorization' : 'Basic ' + base64.b64encode(b'XYZ:432').decode('utf-8')}
        response = self.client.post(reverse('chartreuse:user-list'), {
            'displayName': 'Jane Doe',
            'profileImage': 'https://i.imgur.com/1234.jpeg',
            'username': 'ethankk',
            'password': 'ABC123!!',
            'firstName': 'Jane',
            'lastName': 'Doe',
        }, format='json',headers=cred_of_disabled)

        self.assertEqual(response.status_code,401)

        data = json.loads(response.content)
        self.assertNotEqual(data.get('error'),None)

        user_queryset = AuthUser.objects.filter(username='ethankk')
        self.assertFalse(user_queryset.exists())




