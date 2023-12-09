from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse


class IndexViewTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('index')
    
    def test_index_view_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_index_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)


class SignupViewTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')
        self.template_name = 'accounts/signup.html'
    
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
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')
        self.template_name = 'accounts/login.html'
        
    def test_login_view_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['form'])
    
    @mock.patch("captcha.fields.ReCaptchaField.clean")
    def test_login_view_form_valid_POST(self, mock_clean):
        mock_clean.return_value = "testcaptcha"
        get_user_model().objects.create_user(
            username='test_user',
            password='test_password',
            is_active=True
        )
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
        get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
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
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('logout')
        self.template_name = 'index.html'
        self.test_user = get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        login = self.client.login(username='test_user', password='test_password')
        self.assertTrue(login)
    
    def test_logout_view_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        self.assertTemplateUsed(self.template_name)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class MyProfileViewTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('my_profile')
        self.template_name = 'accounts/my_profile.html'
    
    def test_my_profile_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('accounts/login.html')
        self.assertTemplateNotUsed(self.template_name)

    def test_my_profile_view_as_authenticated_user_GET(self):
        get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url)

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.template_name)
        self.assertIsNotNone(response.context['user_profile'])
    
    def test_my_profile_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(self.template_name)
        

class DeleteUserViewTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
    
    def test_e(self):
        user = self.User.objects.create(username='testuser')
        response = self.client.post(reverse('delete_user', kwargs={'pk': user.pk}))
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        self.assertEqual(str(messages[0]), 'The user has been successfully deleted')
        self.assertFalse(self.User.objects.filter(pk=user.pk).exists())


class PremiumViewTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('premium')
        self.template_name = 'word_bank/premium.html'
    
    def test_premium_view_GET(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
    
    def test_premium_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)


class GetPremiumViewTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('get_premium')
    
    def test_get_premium_view_POST(self):
        test_user = get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url)
        
        test_user.refresh_from_db()

        self.assertTrue(login)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('learn'))
        self.assertTrue(test_user.is_premium)
        
    def test_get_premium_view_method_not_allowed_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class CancelPremiumViewTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('cancel_premium')
        self.url_redirect = reverse('learn')
        
    def test_cancel_premium_view_method_not_allowed_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
    
    def test_cancel_premium_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_redirect)
    
    def test_cancel_premium_view_as_not_premium_user_POST(self):
        test_user = get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url)
        
        test_user.refresh_from_db()

        self.assertTrue(login)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_redirect)
        self.assertFalse(test_user.is_premium)
    
    def test_cancel_premium_view_as_premium_user_POST(self):
        test_user = get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True, is_premium=True
        )
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url)
        
        test_user.refresh_from_db()

        self.assertTrue(login)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_redirect)
        self.assertFalse(test_user.is_premium)
    