from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
from ..models import User
from  urllib.parse import quote


class TestProfileViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        print("In TestProfileViews", User.objects.all())

        cls.client = Client()
        cls.auth_user_1 = AuthUser.objects.create(username='ethankeys',password='ethankisGOAT')
        cls.auth_user_2 = AuthUser.objects.create(username='JuliaD',password='JuliaDisGOAT')
        cls.auth_user_3 = AuthUser.objects.create(username='AllenNestorismybestfriend',password='hestrulyawesome')

        cls.user_1 = User.objects.create(user=cls.auth_user_1,
                           displayName="goatmanethan",
                           github='https://github.com/',
                           url_id = "http://nodeaaaa/api/authors/111"
                           )
        cls.user_2 = User.objects.create(user=cls.auth_user_2,
                           displayName="juliaDtheGOAT",
                           github='https://github.com/',
                           url_id = "http://nodeaaaa/api/authors/222"
                           )
        cls.user_3 = User.objects.create(user=cls.auth_user_3,
                           displayName="allenisagoat",
                           github='https://github.com/',
                           url_id = "http://nodeaaaa/api/authors/333"
                           )
        # setting up each user's id
        cls.user_1_id = quote(cls.user_1.url_id,safe = '')
        cls.user_2_id = quote(cls.user_2.url_id,safe = '')
        cls.user_3_id = quote(cls.user_3.url_id,safe = '')

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()

    # How to Authenticate User in tests: https://www.geeksforgeeks.org/how-to-authenticate-a-user-in-tests-in-django/ (Geeks for Geeks)
    # Article Last Updated on September 25, 2024
    # Purpose: To help authenticate a user each test to check for friendslist viewing permissions.
    def test_viewing_own_friends_list(self):
        self.client.force_login(self.auth_user_1)
    
        response = self.client.get(reverse('chartreuse:user_friends_list', args=[self.user_1_id]))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'follow_list.html')

    def test_viewing_other_friend_list(self):
        self.client.force_login(self.auth_user_1)

        response = self.client.get(reverse('chartreuse:user_friends_list', args=[self.user_2_id]))
        self.assertEqual(response.status_code,403)

    def test_unauthorized_friends_list(self):
        response = self.client.get(reverse('chartreuse:user_friends_list', args=[self.user_2_id]))
        self.assertEqual(response.status_code,401)