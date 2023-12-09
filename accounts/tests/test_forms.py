from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.forms import CustomUserCreationForm, CustomUserLoginForm


class CustomUserCreationFormTestCase(TestCase):
    
    def create_invalid_form(self, error_fields):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@localhost',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        for k, v in error_fields.items():
            form_data[k] = v

        return CustomUserCreationForm(data=form_data)
    
    @mock.patch("captcha.fields.ReCaptchaField.clean")
    def test_custom_user_creation_form_valid_data(self, mock_clean):
        mock_clean.return_value = "testcaptcha"
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'testuser@localhost',
            'password1': 'testpassword',
            'password2': 'testpassword',
        })
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_invalid_captcha(self):
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'testuser@localhost',
            'password1': 'testpassword',
            'password2': 'testpassword',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual('You must pass the reCAPTCHA test', form.errors['captcha'][1])

    def test_custom_user_creation_form_invalid_username_empty(self):
        form = self.create_invalid_form({'username': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual('This field is required.', form.errors['username'][0])

    def test_custom_user_creation_form_invalid_username_contains_spaces(self):
        form = self.create_invalid_form({'username': 'user with spaces'})
        self.assertFalse(form.is_valid())

    def test_custom_user_creation_form_invalid_username_contains_invalid_chars(self):
        form = self.create_invalid_form({'username': 'user@name'})
        self.assertFalse(form.is_valid())
        self.assertEqual('Username contains invalid characters', form.errors['username'][0])

    def test_custom_user_creation_form_invalid_username_too_short(self):
        form = self.create_invalid_form({'username': 'ab'})
        self.assertFalse(form.is_valid())
        self.assertEqual('Username is too short', form.errors['username'][0])

    def test_custom_user_creation_form_invalid_username_too_long(self):
        form = self.create_invalid_form({'username': 'a' * 16})
        self.assertFalse(form.is_valid())

    def test_custom_user_creation_form_invalid_password_too_short(self):
        form = self.create_invalid_form({'password1': 'pass'})
        self.assertFalse(form.is_valid())
        self.assertEqual('Password is too short', form.errors['password1'][0])

    def test_custom_user_creation_form_invalid_passwords_do_not_match(self):
        form = self.create_invalid_form({'password2': 'mismatchedpassword'})
        self.assertFalse(form.is_valid())
        self.assertEqual("The two password fields didn’t match.", form.errors['password2'][0])


class CustomUserLoginFormTestCase(TestCase):
    
    @mock.patch("captcha.fields.ReCaptchaField.clean")
    def test_custom_user_login_form_valid_data(self, mock_clean):
        mock_clean.return_value = "testcaptcha"
        get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        form = CustomUserLoginForm(data={
            'username': 'test_user',
            'password': 'test_password',
        })
        self.assertTrue(form.is_valid())
    
    def test_custom_user_login_form_invalid_captcha(self):
        form = CustomUserLoginForm(data={
            'username': 'test_user',
            'password': 'test_password',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual('You must pass the reCAPTCHA test', form.errors['captcha'][1])
    
    def test_custom_user_login_form_invalid_username(self):
        get_user_model().objects.create_user(
            username='test_user2', password='test_password', is_active=True
        )
        form = CustomUserLoginForm(data={
            'username': 'user_invalid',
            'password': 'test_password',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual('Invalid username or password', form.errors['username'][0])

    def test_custom_user_login_form_invalid_password(self):
        get_user_model().objects.create_user(
            username='test_user3', password='test_password', is_active=True
        )
        form = CustomUserLoginForm(data={
            'username': 'test_user3',
            'password': 'password_invalid',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual('Invalid username or password', form.errors['username'][0])
    
    