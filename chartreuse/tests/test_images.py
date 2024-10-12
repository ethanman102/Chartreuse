from django.test import TestCase, Client
from django.urls import reverse
from ..api_handling import images

class ImageTestCases(TestCase):
    def setUp(self):
        self.client = Client()

        self.test_user_1_data = {
            'displayName': 'Greg Johnson',
            'github': 'http://github.com/gjohnson',
            'profileImage': 'https://kirby.nintendo.com/assets/img/about/char-kirby.png',
            'username': 'greg',
            'password': 'ABC123!!!',
            'host': 'http://nodeaaaa/',
            'firstName': 'Greg',
            'lastName': 'Johnson',
        }

        self.client.post(reverse('chartreuse:user-list'), self.test_user_1_data, format='json')
    
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
        imagePath = 'chartreuse/test_images/buba.jpg'
        
        encoded_string = images.encode_image(imagePath)
        
        # Ensure the string is base64 encoded
        self.assertTrue(isinstance(encoded_string, str))
        self.assertGreater(len(encoded_string), 0)
    
    def test_decode_image(self):
        '''
        Test decoding an image from a base64 string.
        '''
        imagePath = 'chartreuse/test_images/buba.jpg'
        
        encoded_string = images.encode_image(imagePath)
        
        response = images.decode_image(encoded_string)

        # Ensure the response is a binary image
        self.assertTrue(isinstance(response, bytes))