from django.test import TestCase
from django.contrib.auth import get_user_model


class CustomUserModelTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
    
    def test_custom_user_str(self):
        test_user = self.User.objects.create_user(
            username='test_user', is_active=True
        )
        self.assertEqual(str(test_user), 'test_user')
    
    def test_custom_user_save_method_does_not_make_regular_user_active(self):
        test_user_inactive = self.User.objects.create_user(
            username='test_user_inactive'
        )
        self.assertFalse(test_user_inactive.is_active)
    
    def test_custom_user_save_method_makes_staff_user_active(self):
        test_user_staff = self.User.objects.create_user(
            username='test_user_staff', is_staff=True
        )
        self.assertTrue(test_user_staff.is_active)
    
    def test_custom_user_save_method_makes_superuser_active(self):
        test_superuser = self.User.objects.create_user(
            username='test_superuser', is_superuser=True
        )
        self.assertTrue(test_superuser.is_active)
    
    def test_custom_user_user_profile_exists_when_user_is_active(self):
        test_user = self.User.objects.create_user(
            username='test_user', is_active=True
        )
        self.assertTrue(test_user.profile)
    
    def test_custom_user_user_profile_does_not_exist_when_user_is_inactive(self):
        test_user_inactive = self.User.objects.create_user(
            username='test_user_inactive'
        )
        self.assertFalse(test_user_inactive.profile)


class MyProfileTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.test_user = User.objects.create_user(
            username='test_user', is_active=True
        )
        self.test_user_profile = self.test_user.profile

    def test_my_profile_default_values_equal_zero(self):
        self.assertEqual(str(self.test_user_profile), 'Profile test_user')
        self.assertEqual(self.test_user_profile.num_learned_words, 0)
        self.assertEqual(self.test_user_profile.experience, 0)
        self.assertEqual(self.test_user_profile.level, 0)
        self.assertEqual(self.test_user_profile.level_progress, 0)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 1)
    
    def test_my_profile_properties_are_correct(self):
        self.test_user_profile.experience = 70
        self.test_user_profile.save()

        self.assertEqual(self.test_user_profile.experience, 70)
        self.assertEqual(self.test_user_profile.level, 4)
        self.assertAlmostEqual(self.test_user_profile.level_progress, 0.667, places=3)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 10)

    def test_my_profile_properties_change_on_experience_change(self):
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
    
    def test_my_profile_experience_is_negative(self):
        self.test_user_profile.experience = -1
        self.test_user_profile.save()

        self.assertEqual(self.test_user_profile.experience, 0)
        self.assertEqual(self.test_user_profile.level, 0)
        self.assertEqual(self.test_user_profile.level_progress, 0)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 1)
    
    def test_my_profile_experience_overflow_million(self):
        self.test_user_profile.experience = 1_000_000
        self.test_user_profile.save()

        self.assertEqual(self.test_user_profile.experience, 1_000_000)
        self.assertEqual(self.test_user_profile.level, 100)
        self.assertEqual(self.test_user_profile.level_progress, 1)
        self.assertEqual(self.test_user_profile.xp_to_next_level, 0)
    