from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUserToken
from accounts.utils import send_activation_email


class CheckUsernameExistsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('check_username_exists')
        self.request_data = {'username': 'test_user'}
    
    def test_check_username_exists_method_not_allowed_POST(self):
        client = Client()
        response = client.post(self.url, self.request_data)
        self.assertEqual(response.status_code, 405)
    
    def test_check_username_exists_username_available_GET(self):
        response = self.client.get(self.url, self.request_data)
        self.assertEqual(response.status_code, 200)

    def test_check_username_exists_username_taken_GET(self):
        get_user_model().objects.create_user(username='test_user')
        response = self.client.get(self.url, self.request_data)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'exists': True})
    
    def test_check_username_exists_username_empty_GET(self):
        response = self.client.get(self.url, {'username': ''})
        self.assertEqual(response.status_code, 204)


class ActivateUserTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
    
    def test_activate_user_method_not_allowed_POST(self):
        url = reverse('activate_user', args=['foo'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)
        
    def test_activate_user_success_GET(self):
        self.User.objects.filter(username='test_user_activation_success').delete()
        test_user = self.User.objects.create_user(username='test_user_activation_success', password='test_password')
        test_token = CustomUserToken.objects.create(user=test_user, token='test_token').token

        url = reverse('activate_user', args=[test_token])
        response = self.client.get(url)
        
        test_user.refresh_from_db()
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertEqual(test_user.is_active, True)
        
        login = self.client.login(username='test_user_activation_success', password='test_password')
        self.assertTrue(login)
        
    def test_activate_user_failed_invalid_token_GET(self):
        test_user_invalid = self.User.objects.create_user(username='test_user_invalid', password='test_password')
        CustomUserToken.objects.create(user=test_user_invalid, token='test_token')
        
        url = reverse('activate_user', args=['test_invalid_token'])
        response = self.client.get(url)
        
        test_user_invalid.refresh_from_db()
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('signup'))
        self.assertFalse(test_user_invalid.is_active)
        
        login = self.client.login(username='test_user_invalid', password='test_password')
        self.assertFalse(login)
    
    def test_activate_user_failed_expired_token_GET(self):
        test_user_expired = self.User.objects.create_user(username='test_user_expired', password='test_password')
        expire_date = timezone.now()
        CustomUserToken.objects.create(
            user=test_user_expired, token='test_token_expired', expire_date=expire_date
        )
        
        url = reverse('activate_user', args=['test_token_expired'])
        response = self.client.get(url)
        
        test_user_expired.refresh_from_db()
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('signup'))
        self.assertFalse(test_user_expired.is_active)
        self.assertFalse(CustomUserToken.objects.filter(token='test_token_expired').exists())
        
        login = self.client.login(username='test_user_expired', password='test_password')
        self.assertFalse(login)


class SendActivationEmailTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_to_email = 'example@gmail.com'
    
    def test_send_activation_email_success(self):
        test_user = get_user_model().objects.create_user(
            username='test_user', email=self.test_to_email
        )
        success = send_activation_email(user=test_user, to_email=self.test_to_email)
        
        self.assertTrue(success)
