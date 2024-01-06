from django.contrib.auth import get_user_model
from django.test import TestCase, tag

from accounts.models import CustomUserToken, CustomUserTokenType


@tag("accounts", "model", "model_custom_user")
class CustomUserModelTestCase(TestCase):
    fixtures = ['test_users.json', 'test_profiles.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        
        test_users = cls.User.objects.all()
        cls.test_user = test_users.first()
        cls.test_user_staff = test_users.get(username='test_user_staff')
        cls.test_superuser = test_users.get(username='test_superuser')
        cls.test_user_inactive = cls.User.objects.create_user(
            username='test_user_inactive'
        )
    
    def test_custom_user_str(self):
        self.assertEqual(str(self.test_user), 'test_user')
    
    def test_custom_user_save_method_does_not_make_regular_user_active(self):
        self.assertFalse(self.test_user_inactive.is_active)
    
    def test_custom_user_save_method_makes_staff_user_active(self):
        self.assertTrue(self.test_user_staff.is_active)
    
    def test_custom_user_save_method_makes_superuser_active(self):
        self.assertTrue(self.test_superuser.is_active)
    
    def test_custom_user_user_profile_exists_when_user_is_active(self):
        self.assertTrue(self.test_user.profile)
    
    def test_custom_user_user_profile_does_not_exist_when_user_is_inactive(self):
        self.assertFalse(hasattr(self.test_user_inactive, 'profile'))


@tag("accounts", "model", "model_profile")
class ProfileTestCase(TestCase):
    fixtures = ['test_users.json', 'test_profiles.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.test_user = cls.User.objects.first()
        cls.test_user_profile = cls.test_user.profile

    def test_profile_default_values_equal_zero(self):
        self.assertEqual(str(self.test_user_profile), 'Profile test_user')
        self.assertEqual(self.test_user_profile.num_learned_words, 0)
        self.assertEqual(self.test_user_profile.experience, 0)
        self.assertEqual(self.test_user_profile.level, 0)
        self.assertEqual(self.test_user_profile.level_progress, 0)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 1)
    
    def test_profile_properties_are_correct(self):
        self.test_user_profile.experience = 70
        self.test_user_profile.save()

        self.assertEqual(self.test_user_profile.experience, 70)
        self.assertEqual(self.test_user_profile.level, 4)
        self.assertAlmostEqual(self.test_user_profile.level_progress, 0.667, places=3)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 10)

    def test_profile_properties_change_on_experience_change(self):
        self.test_user_profile.experience = 49
        self.test_user_profile.save()

        self.assertEqual(self.test_user_profile.experience, 49)
        self.assertEqual(self.test_user_profile.level, 3)
        self.assertAlmostEqual(self.test_user_profile.level_progress, 0.958, places=3)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 1)
        
        self.test_user_profile.experience += 1
        self.test_user_profile.save()
        
        self.assertEqual(self.test_user_profile.experience, 50)
        self.assertEqual(self.test_user_profile.level, 4)
        self.assertEqual(self.test_user_profile.level_progress, 0)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 30)
    
    def test_profile_experience_is_negative(self):
        self.test_user_profile.experience = -1
        self.test_user_profile.save()

        self.assertEqual(self.test_user_profile.experience, 0)
        self.assertEqual(self.test_user_profile.level, 0)
        self.assertEqual(self.test_user_profile.level_progress, 0)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 1)
    
    def test_profile_experience_overflow_million(self):
        self.test_user_profile.experience = 1_000_000
        self.test_user_profile.save()

        self.assertEqual(self.test_user_profile.experience, 1_000_000)
        self.assertEqual(self.test_user_profile.level, 100)
        self.assertEqual(self.test_user_profile.level_progress, 1)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 0)


@tag("accounts", "model", "model_custom_user_token")
class CustomUserTokenTestCase(TestCase):
    fixtures = ['test_users.json', 'test_token_types.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.test_user = cls.User.objects.first()
        token_type = CustomUserTokenType.objects.get(name='User activation')
        cls.test_user_token = CustomUserToken.objects.create(
            user=cls.test_user,
            token='test_token',
            token_type=token_type
        )
        cls.token = cls.test_user_token.token
    
    def test_custom_user_token_str(self):
        self.assertEqual(str(self.test_user_token), 'test_user - test_token')


@tag("model", "model_custom_user_token_type")
class CustomUserTokenTypeTestCase(TestCase):
    fixtures = ['token_types.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.token_type = CustomUserTokenType.objects.first()
    
    def test_custom_user_token_type_str(self):
        self.assertEqual(str(self.token_type), self.token_type.name)
    
    def test_custom_user_token_type_list_all(self):
        token_types = CustomUserTokenType.objects.all()
        self.assertEqual(len(token_types), 4)
        names = [tt.name for tt in token_types]
        self.assertEqual(names, ['User activation', 'Password reset', 'Username change', 'Email change'])
        