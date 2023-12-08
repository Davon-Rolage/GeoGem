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
    
    def test_signup_view_form_is_invalid_POST(self):
        form_data = {
            'username': 'test_user',
            'email': 'example@gmailcom',
            'password1': 'test_password',
            'password2': '12345',
            'captcha': 'test_captcha',
        }

        response = self.client.post(self.url, data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
    