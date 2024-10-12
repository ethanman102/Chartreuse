from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
from ..models import Follow,FollowRequest,User
from  urllib.parse import quote

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
                           github='https://github.com/',
                           url_id = "http://nodeaaaa/api/authors/111"
                           )
        self.user_2 = User.objects.create(user=self.auth_user_2,
                           displayName="juliaDtheGOAT",
                           github='https://github.com/',
                           url_id = "http://nodeaaaa/api/authors/222"
                           )
        self.user_3 = User.objects.create(user=self.auth_user_3,
                           displayName="allenisagoat",
                           github='https://github.com/',
                           url_id = "http://nodeaaaa/api/authors/333"
                           )
        # setting up each user's id
        self.user_1_id = quote(self.user_1.url_id,safe = '')
        self.user_2_id = quote(self.user_2.url_id,safe = '')
        self.user_3_id = quote(self.user_3.url_id,safe = '')

        # Setting up follow request
        self.follow_request_1 = FollowRequest.objects.create(requestee=self.user_1,requester=self.user_2)
        self.follow_1 = Follow.objects.create(followed=self.user_3,follower=self.user_1)

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
        follow_request = FollowRequest.objects.filter(requestee=self.user_1,requester=self.user_2)
        self.assertEqual(follow_request.exists(),False)
    
    '''
    Checking Acceptance of Follow Request
    '''
    
    def test_follow_accept(self):
        response = self.client.post(reverse('chartreuse:profile_follow_accept', args=[self.user_1_id,self.user_2_id]))
        self.assertEqual(response.status_code,302)
        follow_request = FollowRequest.objects.filter(requestee=self.user_1,requester=self.user_2)
        self.assertEqual(follow_request.exists(),False)
        follow = Follow.objects.filter(followed=self.user_1,follower=self.user_2)
        self.assertEqual(follow.exists(),True)
        self.assertEqual(follow.count(),1)

    '''

    Tests for checking the template view (detail view)

    '''
    def test_profile_template_used(self):
        response = self.client.get(reverse('chartreuse:profile',args=[self.user_1_id]))
        self.assertTemplateUsed(response,'profile.html')
    
    def test_profile_template_context(self):

        response = self.client.get(reverse('chartreuse:profile',args=[self.user_3_id]))
        self.assertTemplateUsed(response,'profile.html')

        data = response.content
        data = data.decode()

        self.assertEqual('allenisagoat' in data,True)
        self.assertEqual('Following 0' in data, True)
        self.assertEqual('Followers 1' in data,True)
    
    '''
    
    Tests for unfollowing an author and sending in follow requests!

    '''

    def test_unfollow_invalid_method(self):
        response = self.client.get(reverse('chartreuse:profile_unfollow'),args=[self.user_3_id,self.user_1_id])
        self.assertEqual(response.status_code,405)

    def test_send_follow_request_invalid_method(self):
        response = self.client.get(reverse('chartreuse:profile_follow_request'),args=[self.user_3_id,self.user_1_id])
        self.assertEqual(response.status_code,405)

    def test_unfollow(self):
        response = self.client.post(reverse('chartreuse:profile_unfollow'),args=[self.user_3_id,self.user_1_id])
        self.assertEqual(response.status_code,302)
        # check that follow has been removed
        follow = Follow.objects.filter(follower=self.user_1,followed=self.user_3).count()
        self.assertEqual(follow,0)
        # check that UI updated to remove the follower!
        response = self.client.get(reverse('chartreuse:profile',args=[self.user_3_id]))
        self.assertTemplateUsed(response,'profile.html')
        data = response.content
        data = data.decode()
        self.assertEqual('Followers 0' in data,True)

    def test_profile_send_follow_request(self):
        response = self.client.post(reverse('chartreuse:profile_follow_request'),args=[self.user_2_id,self.user_3_id])

        self.assertEqual(response.status_code,302)
        follow_request = FollowRequest.objects.filter(requester=self.user_2,requestee=self.user_3).count()
        self.assertEqual(follow_request,1)

  
        
