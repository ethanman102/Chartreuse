from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
from .models import Follow,FollowRequest,User

class TestProfileViews(TestCase):

    def setUp(self):
        self.client = Client()

        self.auth_user_1 = AuthUser.objects.create(username='ethankeys',password='ethankisGOAT')
        self.auth_user_2 = AuthUser.objects.create(username='JuliaD',password='JuliaDisGOAT')
        self.auth_user_3 = AuthUser.objects.create(username='AllenNestorismybestfriend',password='hestrulyawesome')

        self.user_1 = User.objects.create(user=self.auth_user_1,
                           displayName="goatmanethan",
                           github='https://github.com/'
                           )
        self.user_2 = User.objects.create(user=self.auth_user_2,
                           displayName="juliaDtheGOAT",
                           github='https://github.com/'
                           )
        self.user_3 = User.objects.create(user=self.auth_user_3,
                           displayName="allenisagoat",
                           github='https://github.com/'
                           )
        
        self.user_1_id = self.user_1.user.id
        self.user_2_id = self.user_2.user.id
        self.user_3_id = self.user_3.user.id

    def test_follow_accept_method_not_allowed(self):
        response = self.client.get(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id,self.user_2_id]))
        self.assertEqual(response.status_code,405) # equivalence class of tests is checking other methods other than post.
        
    
    def test_follow_reject_method_not_allowed(self):
        response = self.client.get(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id,self.user_2_id]))
        self.assertEqual(response.status_code,405) # equivalence class of tests is checking other methods other than post.
    
    def test_follow_accept_invalid_requestee(self):
        response = self.client.post(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id + self.user_2_id + self.user_3_id,self.user_2_id]))
        self.assertEqual(response.status_code,404)

    def test_follow_reject_invalid_requestee(self):
        response = self.client.post(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id + self.user_2_id + self.user_3_id,self.user_2_id]))
        self.assertEqual(response.status_code,404)

        
