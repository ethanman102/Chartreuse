from django.test import TestCase, Client
from django.urls import reverse
from ..api_handling import images
from ..models import User

class ImageTestCases(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()

        cls.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://kirby.nintendo.com/assets/img/about/char-kirby.png',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': 'http://nodeaaaa/',
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        cls.client.post(reverse('chartreuse:user-list'), cls.test_user_1_data, format='json')
        cls.imagePath = 'chartreuse/static/images/buba.jpg'

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()
    
    def test_encode_image_from_url(self):
        '''
        Test encoding an image from a url.
        '''
        userProfileImagePath = self.test_user_1_data['profileImage']

        encoded_string = images.encode_image(userProfileImagePath)
        
        # Ensure the string is base64 encoded
        self.assertTrue(isinstance(encoded_string, str))
        self.assertGreater(len(encoded_string), 0)

    def test_encode_image_from_file(self):
        '''
        Test encoding an image from a file path.
        '''        
        encoded_string = images.encode_image(self.imagePath)
        
        # Ensure the string is base64 encoded
        self.assertTrue(isinstance(encoded_string, str))
        self.assertGreater(len(encoded_string), 0)
    
    def test_decode_image(self):
        '''
        Test decoding an image from a base64 string.
        '''        
        encoded_string = images.encode_image(self.imagePath)
        
        response = images.decode_image(encoded_string)

        # Ensure the response is a binary image
        self.assertTrue(isinstance(response, bytes))