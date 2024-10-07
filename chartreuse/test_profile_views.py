from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
from .models import Follow,FollowRequest,User

'''
Resource: Help in understanding how to test Django views was utilized through this Youtube informational video: https://www.youtube.com/watch?time_continue=570&v=hA_VxnxCHbo&embeds_referring_euri=https%3A%2F%2Fwww.bing.com%2F&embeds_referring_origin=https%3A%2F%2Fwww.bing.com&source_ve_path=MzY4NDIsMTM5MTE3LDI4NjYzLDEzOTExNywxMzkxMTcsMTM5MTE3LDIzODUx
# Author of Video: The Dumbfounds(https://www.youtube.com/@thedumbfounds767)
# Posted: December 18, 2018
# Accessed: October 7, 2024

'''
class TestProfileViews(TestCase):

    def setUp(self):
        self.client = Client()
        # Setting up authentication Users
        self.auth_user_1 = AuthUser.objects.create(username='ethankeys',password='ethankisGOAT')
        self.auth_user_2 = AuthUser.objects.create(username='JuliaD',password='JuliaDisGOAT')
        self.auth_user_3 = AuthUser.objects.create(username='AllenNestorismybestfriend',password='hestrulyawesome')

        # setting up user's model
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
        # setting up each user's id
        self.user_1_id = self.user_1.user.id
        self.user_2_id = self.user_2.user.id
        self.user_3_id = self.user_3.user.id

        # Setting up follow request
        self.follow_request_1 = FollowRequest.objects.create(requestee=self.user_1,requester=self.user_2)

    def test_follow_accept_method_not_allowed(self):
        response = self.client.get(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id,self.user_2_id]))
        self.assertEqual(response.status_code,405) # equivalence class of tests is checking other methods other than post.
        
    
    def test_follow_reject_method_not_allowed(self):
        response = self.client.get(reverse('chartreuse:profile_follow_reject', args=[self.user_1_id,self.user_2_id]))
        self.assertEqual(response.status_code,405) # equivalence class of tests is checking other methods other than post.

    '''
    Invalid person id being followed tests
    '''
    
    def test_follow_accept_invalid_requestee(self):
        response = self.client.post(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id + self.user_2_id + self.user_3_id,self.user_2_id]))
        self.assertEqual(response.status_code,404)

    def test_follow_reject_invalid_requestee(self):
        response = self.client.post(reverse('chartreuse:profile_follow_reject', args=[self.user_1_id + self.user_2_id + self.user_3_id,self.user_2_id]))
        self.assertEqual(response.status_code,404)

    '''
    Invalid person id following tests
    '''

    def test_follow_accept_invalid_requester(self):
        response = self.client.post(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id,self.user_1_id + self.user_2_id + self.user_3_id]))
        self.assertEqual(response.status_code,404)
    
    def test_follow_reject_invalid_requester(self):
        response = self.client.post(reverse('chartreuse:profile_follow_reject', args=[self.user_1_id,self.user_1_id + self.user_2_id + self.user_3_id]))
        self.assertEqual(response.status_code,404)

    '''
    Invalid Follow Request Tests (Ex: The User's exist but the follow request does now!)
    '''

    def test_follow_accept_invalid_request(self):
        response = self.client.post(reverse('chartreuse:profile_follow_accept', args=[self.user_2_id,self.user_3_id]))
        self.assertEqual(response.status_code,404)

    def test_follow_reject_invalid_request(self):
        response = self.client.post(reverse('chartreuse:profile_follow_reject', args=[self.user_2_id,self.user_3_id]))
        self.assertEqual(response.status_code,404)

    '''
    Checking Rejection of Follow Request (Ex: request is deleted and no follower in db)
    '''

    def test_follow_reject(self):
        response = self.client.post(reverse('chartreuse:profile_follow_reject', args=[self.user_1_id,self.user_2_id]))
        self.assertEqual(response.status_code,302)
        follow_request = FollowRequest.objects.filter(requestee=self.user_1_id,requester=self.user_2_id)
        self.assertEqual(follow_request.exists(),False)
    
    '''
    Checking Acceptance of Follow Request
    '''
    
    def test_follow_accept(self):
        response = self.client.post(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id,self.user_2_id]))
        self.assertEqual(response.status_code,302)
        follow_request = FollowRequest.objects.filter(requestee=self.user_1_id,requester=self.user_2_id)
        self.assertEqual(follow_request.exists(),False)
        follow = Follow.objects.filter(followed=self.user_1_id,follower=self.user_2_id)
        self.assertEqual(follow.exists(),True)
        self.assertEqual(follow.count(),1)

        

        
