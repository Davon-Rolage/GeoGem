from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.test import TestCase
from django.urls import reverse

from word_bank.models import Block, UserWord, WordInfo


class LearnListViewTestCase(TestCase):
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('learn')
        cls.template_name = 'word_bank/learn.html'
        
        cls.test_block = Block.objects.first()
        cls.test_user = cls.User.objects.first()
        cls.test_user_profile = cls.test_user.profile

    def test_learn_list_view_as_anonymous_user(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn(self.test_block, response.context['learning_blocks'])

    def test_learn_list_view_as_authenticated_user_GET(self):
        self.test_user_profile.experience = 20
        self.test_user_profile.save()
        
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)
        
        self.test_user_profile.refresh_from_db(fields=['experience'])
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(self.test_user_profile.experience, 20)
        self.assertEqual(self.test_user_profile.level, 2)
        self.assertIn(self.test_block, response.context['learning_blocks'])
        

class BlockDetailViewTestCase(TestCase):
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('block_detail', args=['test-block'])
        cls.template_name = 'word_bank/block_detail.html'

        cls.test_user = cls.User.objects.first()
        cls.test_user_all_words_learned = cls.User.objects.get(username='test_user_all_words_learned')
        
    def test_block_detail_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], int)
        self.assertEqual(response.context['block_mastery_level'], 0)
        self.assertFalse(response.context['learning_block'].is_completed)

    def test_block_detail_view_as_authenticated_user_GET(self):        
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEqual(response.context['block_mastery_level'], 0.2)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertFalse(response.context['learning_block'].is_completed)
    
    def test_block_detail_view_as_user_with_completed_block_GET(self):
        self.client.force_login(self.test_user_all_words_learned)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEqual(response.context['block_mastery_level'], 1.0)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertTrue(response.context['learning_block'].is_completed)


class EditBlocksViewTestCase(TestCase):
    fixtures = ['test_users.json', 'test_blocks.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('blocks_table')
        cls.template_name = 'word_bank/blocks_table.html'

        cls.test_block = Block.objects.first()
        cls.test_user = cls.User.objects.first()
        cls.test_user_staff = cls.User.objects.get(username='test_user_staff')
            
    def test_edit_blocks_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)

    def test_edit_blocks_view_as_unauthorized_user_GET(self):
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_edit_blocks_view_as_staff_GET(self):
        self.client.force_login(self.test_user_staff)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['blocks'])
        self.assertIsInstance(response.context['blocks'], QuerySet)
        self.assertIn(self.test_block, response.context['blocks'])
    

class EditBlockDetailViewTestCase(TestCase):
    fixtures = ['test_users.json', 'test_blocks.json', 'test_word_infos.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('block_edit', args=['test-block'])
        cls.template_name = 'word_bank/block_edit.html'

        cls.test_user_staff = cls.User.objects.get(username='test_user_staff')
        cls.test_word_info = WordInfo.objects.first()

    def test_edit_block_detail_view_as_unauthorized_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_edit_block_detail_view_as_staff_GET(self):
        self.client.force_login(self.test_user_staff)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsInstance(response.context['block_words'], QuerySet)
        self.assertIn(self.test_word_info, response.context['block_words'])


class AddWordInfoViewTestCase(TestCase):
    fixtures = [
        'test_users.json', 'test_blocks.json', 'test_word_infos.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('add_word_info')

        cls.test_block = Block.objects.first()
        cls.request_data = {'learning_block_id': cls.test_block.id}
        cls.test_user = cls.User.objects.first()
        cls.test_user_staff = cls.User.objects.get(username='test_user_staff')
    
    def test_add_word_info_view_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
    
    def test_add_word_info_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, data=self.request_data)
        self.assertEqual(response.status_code, 302)
        
    def test_add_word_info_view_as_unauthorized_user_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, data=self.request_data)

        self.assertEqual(response.status_code, 302)
    
    def test_add_word_info_view_as_staff_POST(self):
        self.client.force_login(self.test_user_staff)
        response = self.client.post(self.url, data=self.request_data)
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {'success': True})


class EditWordInfoViewTestCase(TestCase):
    fixtures = ['test_users.json', 'test_blocks.json', 'test_word_infos.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('edit_word_info')

        cls.test_word_info = WordInfo.objects.first()
        cls.request_data = {
            'word_id': cls.test_word_info.id,
            'changed_field': 'translation',
            'new_value': 'New Translation'
        }
        cls.test_user = cls.User.objects.first()
        cls.test_user_staff = cls.User.objects.get(username='test_user_staff')

    def test_edit_word_info_view_method_not_allowed_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        
    def test_edit_word_info_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, data=self.request_data)
        self.assertEqual(response.status_code, 302)
        
    def test_edit_word_info_view_as_unauthorized_user_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, data=self.request_data)

        self.assertEqual(response.status_code, 302)
    
    def test_edit_word_info_view_as_staff_POST(self):
        self.client.force_login(self.test_user_staff)
        old_value = self.test_word_info.translation

        response = self.client.post(self.url, data=self.request_data)
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {
            'success': True,
            'word_id': str(self.request_data['word_id']),
            'changed_field': self.request_data['changed_field'], 
            'old_value': old_value,
            'new_value': self.request_data['new_value'],
            'updated_at': self.test_word_info.updated_at.strftime('%H:%M:%S %d-%m-%Y')
        })


class UserWordsListViewTestCase(TestCase):
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('user_words')
        cls.template_name = 'word_bank/user_words.html'
        
        cls.test_user = cls.User.objects.first()
        cls.test_user_word = UserWord.objects.first()

    def test_user_words_list_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_user_words_list_view_as_authenticated_user_GET(self):
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)
        response_words = response.context['words']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsInstance(response_words, QuerySet)
        self.assertIn(self.test_user_word, response_words)


class UserBlockDetailViewTestCase(TestCase):
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('user_block_detail', args=['test-block'])
        cls.template_name = 'word_bank/user_block_detail.html'

        cls.test_user = cls.User.objects.first()
        cls.test_user_word_count = UserWord.objects.filter(user=cls.test_user).count()

    def test_user_block_detail_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(len(response.context['words']), 0)

    def test_user_block_detail_view_as_authenticated_user_GET(self):
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)
        response_words = response.context['words']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsInstance(response_words, QuerySet)
        self.assertEqual(len(response_words), self.test_user_word_count)
        
    def test_user_block_detail_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)


class AboutViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('about')
        cls.template_name = 'word_bank/about.html'
    
    def test_about_view_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.template_name)
    
    def test_about_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(self.template_name)


class ResetTestBlockViewTestCase(TestCase):
    fixtures = ['test_users.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('reset_test_block')

        cls.test_user = cls.User.objects.first()
        cls.test_user_staff = cls.User.objects.get(username='test_user_staff')
    
    def test_reset_test_block_view_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
    
    def test_reset_test_block_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_reset_test_block_view_as_unauthorized_user_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
    
    def test_reset_test_block_view_as_staff_POST(self):
        self.client.force_login(self.test_user_staff)
        response = self.client.post(self.url)
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {'success': True})
    