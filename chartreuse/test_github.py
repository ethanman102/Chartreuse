# from django.test import TestCase, Client
# from django.urls import reverse
# from urllib.parse import quote

# class LikeTestCases(TestCase):
#     def setUp(self):
#         self.client = Client()

#         # Test user data
#         self.test_user_1_data = {
#             'displayName': 'Julia',
#             'github': 'http://github.com/Julia-Dantas',
#             'profileImage': 'https://i.imgur.com/k7XVwpB.jpeg',
#             'username': 'julia',
#             'password': 'ABC123!!!',
#             'host': 'http://nodeaaaa/',
#             'firstName': 'Julia',
#             'lastName': 'Dantas',
#         }

#         self.client.post(reverse('chartreuse:user-list'), self.test_user_1_data, format='json')
    
#     def test_get_events(self):
#         '''
#         This tests getting a users git events.
#         '''
#         user_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
#         response = self.client.get(reverse('chartreuse:get_events', args=[user_id]))

#         # Successfully got response
#         self.assertEqual(response.status_code, 200)
    
#     def test_get_starred(self):
#         '''
#         This tests getting a users starred repos.
#         '''
#         user_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
#         response = self.client.get(reverse('chartreuse:get_starred', args=[user_id]))

#         # Successfully got response
#         self.assertEqual(response.status_code, 200)
    
#     def test_get_subscriptions(self):
#         '''
#         This tests getting a users watched repos.
#         '''
#         user_id = quote("https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/authors/1", safe='')
#         response = self.client.get(reverse('chartreuse:get_subscriptions', args=[user_id]))

#         # Successfully got response
#         self.assertEqual(response.status_code, 200)