from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse


class IndexViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('index')
    
    def test_index_view_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_index_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)


class SignupViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('signup')
        cls.template_name = 'accounts/signup.html'
    
    def test_signup_view_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['form'])
    
    @mock.patch("captcha.fields.ReCaptchaField.clean")
    def test_signup_view_form_valid_POST(self, mock_clean):
        mock_clean.return_value = "testcaptcha"
        form_data = {
            'username': 'test_user',
            'email': 'example@gmail.com',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        response = self.client.post(self.url, data=form_data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertIn('alert-success', response.content.decode('utf-8'))
    
    def test_signup_view_form_invalid_POST(self):
        form_data = {
            'username': 'test_user',
            'email': 'example@gmail.com',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        response = self.client.post(self.url, data=form_data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn('alert-danger', response.content.decode('utf-8'))
        self.assertIsNotNone(response.context['form'])


class LoginViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('login')
        cls.template_name = 'accounts/login.html'
        
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        
    def test_login_view_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['form'])
    
    @mock.patch("captcha.fields.ReCaptchaField.clean")
    def test_login_view_form_valid_POST(self, mock_clean):
        mock_clean.return_value = "testcaptcha"
        form_data = {
            'username': 'test_user',
            'password': 'test_password',
        }
        response = self.client.post(self.url, data=form_data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_login_view_form_invalid_POST(self):
        form_data = {
            'username': 'test_user',
            'password': 'test_password',
        }
        response = self.client.post(self.url, data=form_data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn('alert-danger', response.content.decode('utf-8'))
        self.assertIsNotNone(response.context['form'])
    
    @mock.patch("captcha.fields.ReCaptchaField.clean")
    def test_login_view_form_valid_wrong_credentials_POST(self, mock_clean):
        mock_clean.return_value = "testcaptcha"
        form_data = {
            'username': 'test_user',
            'password': 'wrong_password',
        }
        response = self.client.post(self.url, data=form_data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn('alert-danger', response.content.decode('utf-8'))
        self.assertIsNotNone(response.context['form'])


class LogoutViewTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('logout')
        self.template_name = 'index.html'
        
        self.test_user = self.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        
    def test_logout_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertTemplateUsed('index.html')
    
    def test_logout_view_as_authenticated_user_GET(self):
        login = self.client.login(username='test_user', password='test_password')
        self.assertTrue(login)
        
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertTemplateUsed(self.template_name)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class MyProfileViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('my_profile')
        cls.template_name = 'accounts/my_profile.html'
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
    
    def test_my_profile_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(self.template_name)
        
    def test_my_profile_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('accounts/login.html')
        self.assertTemplateNotUsed(self.template_name)

    def test_my_profile_view_as_authenticated_user_GET(self):
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.template_name)
        self.assertIsNotNone(response.context['user_profile'])
        

class DeleteUserViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()

        cls.test_user = cls.User.objects.create(username='testuser')
        cls.url = reverse('delete_user', kwargs={'pk': cls.test_user.pk})
        cls.template_name_redirect = 'index.html'
    
    def test_delete_user_view_as_logged_in_user(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, follow=True)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed = self.template_name_redirect
        self.assertEqual(str(messages[0]), 'The user has been successfully deleted')
        self.assertFalse(self.User.objects.filter(pk=self.test_user.pk).exists())


class PremiumViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('premium')
        cls.template_name = 'word_bank/premium.html'
    
    def test_premium_view_GET(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
    
    def test_premium_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)


class GetPremiumViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('get_premium')
        
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_premium = cls.User.objects.create_user(
            username='test_user_premium', password='test_password',
            is_active=True, is_premium=True
        )
    
    def test_get_premium_view_method_not_allowed_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_premium_view_was_not_premium_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url)
        
        self.test_user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('learn'))
        self.assertTrue(self.test_user.is_premium)
    
    def test_get_premium_view_was_premium_POST(self):
        self.client.force_login(self.test_user_premium)
        response = self.client.post(self.url)
        
        self.test_user_premium.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('learn'))
        self.assertTrue(self.test_user_premium.is_premium)


class CancelPremiumViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        
        cls.url = reverse('cancel_premium')
        cls.url_redirect = reverse('learn')
        cls.template_name_redirect = 'word_bank/learn.html'
        
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_premium = cls.User.objects.create_user(
            username='test_user_premium', password='test_password',
            is_active=True, is_premium=True
        )
        
    def test_cancel_premium_view_method_not_allowed_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
    
    def test_cancel_premium_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.url_redirect)
        self.assertTemplateUsed(response, self.template_name_redirect)
    
    def test_cancel_premium_view_as_not_premium_user_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, follow=True)
        
        self.test_user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.url_redirect)
        self.assertFalse(self.test_user.is_premium)
        self.assertTemplateUsed(response, self.template_name_redirect)
    
    def test_cancel_premium_view_as_premium_user_POST(self):
        self.client.force_login(self.test_user_premium)
        response = self.client.post(self.url, follow=True)
        
        self.test_user_premium.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.url_redirect)
        self.assertFalse(self.test_user_premium.is_premium)
        self.assertTemplateUsed(response, self.template_name_redirect)
