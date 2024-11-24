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

        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json',headers=cls.creds)




    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()