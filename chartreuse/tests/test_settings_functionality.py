from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import check_password
from ..models import User, Post
from django.core.files.uploadedfile import SimpleUploadedFile
import base64



class TestSettingsViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.auth_user_1 = AuthUser.objects.create_user(username='ethankeys',password='@#goatMan102ERK')
        self.auth_user_2 = AuthUser.objects.create_user(username="ethanman102",password="chartreusyEthanMan10&$!")

        self.user_1 = User.objects.create(user=self.auth_user_1,
            displayName="goatmanethan",
            github='https://github.com/',
            url_id = "http://nodeaaaa/api/authors/111"
        )

        self.user_2 = User.objects.create(user=self.auth_user_2,displayName='ethankeysboy',github=None,url_id="http://nodeaaaa/api/authors/222")
        

    def test_incorrect_old_password(self):
        self.client.force_login(self.auth_user_1)
        # https://stackoverflow.com/questions/31902901/django-test-client-method-override-header
        # Django Test Client Method Override Header
        # Purpose of use case of Stack Overflow Post: HOW TO SET CONTENT TYPE HEADER OF REVERSE POST COMMAND 
        # Reason: to allow json.loads to work in the views
        # Answered by: Rahul Gupta August 9 2015

        response = self.client.post(reverse('chartreuse:update_password'), {
            'old_pass': 'thispass!sucksSOMUCH',
            'new_pass': 'literallyWhyEthan!isSoGOOD'
        },content_type='application/json')

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
        },content_type='application/json') 

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
        },content_type='application/json') 

        self.assertEqual(response.status_code,200)
        updated = AuthUser.objects.get(username='ethankeys')

        unchanged_pass = updated.check_password('@#goatMan102ERK')
        changed_pass = updated.check_password('well60!!EthanCool')

        self.assertEqual(unchanged_pass,False)
        self.assertEqual(changed_pass,True)

    def test_display_name_changed(self):
        self.client.force_login(self.auth_user_1)

        response = self.client.post(reverse('chartreuse:update_display_name'),{
            'display_name': "chartreuseSauce"
        },content_type='application/json')

        updated = User.objects.get(user=self.auth_user_1)

        self.assertEqual(response.status_code,200)
        self.assertNotEqual("goatmanethan",updated.displayName)
        self.assertEqual("chartreuseSauce",updated.displayName)

    def test_removing_github(self):
        self.client.force_login(self.auth_user_1)
        response = self.client.delete(reverse('chartreuse:remove_github'),{
            'current_github': self.user_1.github
        },content_type='application/json')

        self.assertEqual(response.status_code, 200)

        updated = User.objects.get(user=self.auth_user_1)
        self.assertEqual(updated.github,None)

    def test_server_github_remove_error(self):

        self.client.force_login(self.auth_user_1)
        response = self.client.delete(reverse('chartreuse:remove_github'),{
            'current_github': 'thisShouldRaiseAnErroForUnMatchingCurrentGithub'
        },content_type='application/json')
    
        self.assertEqual(response.status_code,500)
        updated = User.objects.get(user=self.auth_user_1)

        self.assertEqual(updated.github,'https://github.com/')

    
    def test_add_github(self):
        self.client.force_login(self.auth_user_2)
        response = self.client.put(reverse('chartreuse:add_github'),{
            'github': 'https://github.com/'
        },content_type='application/json')

        self.assertEqual(response.status_code,200)
        updated = User.objects.get(user=self.auth_user_2)

        self.assertEqual(updated.github,'https://github.com/')

    
    def test_reject_non_github(self):
        self.client.force_login(self.auth_user_2)
        response = self.client.put(reverse('chartreuse:add_github'),{
            'github': 'HORRIBLEURL'
        },content_type='application/json')

        self.assertEqual(response.status_code,400)

        updated = User.objects.get(user=self.auth_user_2)

        self.assertEqual(updated.github,None)

    def test_add_github_method_not_allowed(self):
        self.client.force_login(self.auth_user_2)
        response = self.client.post(reverse('chartreuse:add_github'),{
            'github': 'HORRIBLEURL'
        },content_type='application/json')

        self.assertEqual(response.status_code,405)
    
    def test_remove_github_method_not_allowed(self):
        self.client.force_login(self.auth_user_2)
        response = self.client.get(reverse('chartreuse:remove_github'),{
            'github': 'HORRIBLEURL'
        },content_type='application/json')

        self.assertEqual(response.status_code,405)

    def test_change_display_name_method_not_allowed(self):
        self.client.force_login(self.auth_user_2)
        response = self.client.get(reverse('chartreuse:update_display_name'),{
            'github': 'HORRIBLEURL'
        },content_type='application/json')

        self.assertEqual(response.status_code,405)

    def test_update_password_method_not_allowed(self):
        self.client.force_login(self.auth_user_2)
        response = self.client.get(reverse('chartreuse:update_password'),{
            'github': 'HORRIBLEURL'
        },content_type='application/json')

        self.assertEqual(response.status_code,405)

    def test_upload_picture_not_allowed(self):
        self.client.force_login(self.auth_user_2)
        response = self.client.put(reverse('chartreuse:upload_profile_picture'),{
            'file':open('chartreuse/static/images/buba.jpg')
        })

        self.assertEqual(response.status_code,405)

    def test_upload_file_no_file(self):
        self.client.force_login(self.auth_user_2)
        response = self.client.post(reverse('chartreuse:upload_profile_picture'))

        self.assertEqual(response.status_code,400)

    def test_upload_picture_OK(self):
        self.client.force_login(self.auth_user_2)
        # https://stackoverflow.com/questions/11170425/how-to-unit-test-file-upload-in-django
        # Stack overflow post: HOW TO UNIT TEST FILE UPLOAD IN DJANGO
        # purpose: how to send a mock image to the api, and test it's ability to change profile post.
        # simpleuploadedfile method utilized from author: Danilo Cabello (posted answer December 7, 2014)
        image = SimpleUploadedFile("test.png",b"file_content",content_type='image/png')
        response = self.client.post(reverse('chartreuse:upload_profile_picture'),{
            'file':image
        })

        encoded_image = base64.b64encode(b'file_content').decode('utf-8')
        

        self.assertEqual(response.status_code,200)
        data = response.json()
        self.assertEqual(data.get('image'),encoded_image)

        new_image = Post.objects.filter(user=self.user_2)

        self.assertEqual(new_image.count(),1)
        new_image = new_image.first()
        self.assertEqual(new_image.content,encoded_image)
        
        updated = User.objects.get(user=self.auth_user_2)

        self.assertEqual(updated.profileImage,new_image.url_id + '/image')

        









        

        
        
    
    

        



