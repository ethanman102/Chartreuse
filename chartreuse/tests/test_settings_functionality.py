from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import check_password


class TestProfileViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.auth_user_1 = AuthUser.objects.create_user(username='ethankeys',password='@#goatMan102ERK')

    def test_incorrect_old_password(self):
        self.client.force_login(self.auth_user_1)
        
        response = self.client.post(reverse('chartreuse:update_password'), {
            'old_pass': 'thispass!sucksSOMUCH',
            'new_pass': 'literallyWhyEthan!isSoGOOD'
        })

        self.assertEqual(response.status_code,403)
        updated = AuthUser.objects.get(username='ethankeys')

        unchanged_pass = updated.check_password('@#goatMan102ERK')
        changed_pass = updated.check_password('well60!!EthanCool')
        self.assertEqual(unchanged_pass,True)
        self.assertEqual(changed_pass,False)

    def test_unvalidated_password(self):
        self.client.force_login(self.auth_user_1)
        
        response = self.client.post(reverse('chartreuse:update_password'), {
            'old_pass': '@#goatMan102ERK',
            'new_pass': '1'
        }) 

        self.assertEqual(response.status_code,400)
        updated = AuthUser.objects.get(username='ethankeys')

        unchanged_pass = updated.check_password('@#goatMan102ERK')
        changed_pass = updated.check_password('well60!!EthanCool')

        self.assertEqual(unchanged_pass,True)
        self.assertEqual(changed_pass,False)
    
    def test_password_change(self):
        self.client.force_login(self.auth_user_1)
        
        response = self.client.post(reverse('chartreuse:update_password'), {
            'old_pass': '@#goatMan102ERK',
            'new_pass': 'well60!!EthanCool'
        }) 

        self.assertEqual(response.status_code,200)
        updated = AuthUser.objects.get(username='ethankeys')

        unchanged_pass = updated.check_password('@#goatMan102ERK')
        changed_pass = updated.check_password('well60!!EthanCool')

        self.assertEqual(unchanged_pass,False)
        self.assertEqual(changed_pass,True)



