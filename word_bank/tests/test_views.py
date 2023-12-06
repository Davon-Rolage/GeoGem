from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import MyProfile
from word_bank.models import Block, UserWord, WordInfo


class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        
        self.test_block = Block.objects.create(id=0, name='Test Block', is_visible=True)
        self.test_word_info = WordInfo.objects.create(name='Test Word', translation='Test Word Translation')
        self.test_word_info.blocks.add(self.test_block)
        self.test_word_info2 = WordInfo.objects.create(name='Test Word 2', translation='Test Word 2 Translation')
        self.test_word_info2.blocks.add(self.test_block)
        
        self.test_superuser = get_user_model().objects.create_superuser(
            username='test_superuser', password='test_password', is_active=True
        )
        self.test_user = get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        self.test_profile = MyProfile.objects.create(user=self.test_user)
        self.test_profile.experience = 20
        self.test_profile.save()
        self.test_user_word = UserWord.objects.create(user=self.test_user, word=self.test_word_info, points=1)

        self.test_user_complete_block = get_user_model().objects.create_user(
            username='test_user_complete_block', password='test_password', is_active=True
        )
        for word in WordInfo.objects.all():
            UserWord.objects.create(user=self.test_user_complete_block, word=word, points=1)
        
        self.url_learn = reverse('learn')
        self.url_about = reverse('about')
        self.url_user_words = reverse('user_words')
        self.url_user_block_detail = reverse('user_block_detail', args=['test-block'])
        self.url_add_word_info = reverse('add_word_info')
        self.url_edit_word_info = reverse('edit_word_info')
        self.url_blocks_table =reverse('blocks_table')
        self.url_reset_test_block = reverse('reset_test_block')
        self.url_block_detail = reverse('block_detail', args=['test-block'])
        self.url_block_edit = reverse('block_edit', args=['test-block'])
        
        self.template_name_learn = 'word_bank/learn.html'
        self.template_name_about = 'word_bank/about.html'
        self.template_name_user_words = 'word_bank/user_words.html'
        self.template_name_user_block_detail = 'word_bank/user_block_detail.html'
        self.template_name_blocks_table = 'word_bank/blocks_table.html'
        self.template_name_reset_test_block = 'word_bank/reset_test_block.html'
        self.template_name_block_detail = 'word_bank/block_detail.html'
        self.template_name_block_edit = 'word_bank/block_edit.html'

    def test_learn_list_view_with_authenticated_user_GET(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url_learn)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_learn)
        self.assertEquals(response.context['user'].experience, 20)
        self.assertEquals(response.context['user'].level, 2)
        self.assertIn(self.test_block, response.context['learning_blocks'])
        
    def test_learn_list_view_with_anonymous_user(self):
        self.client.logout()
        response = self.client.get(self.url_learn)
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_learn)
        self.assertEquals(response.context['user'].experience, 0)
        self.assertEquals(response.context['user'].level, 0)
        self.assertIn(self.test_block, response.context['learning_blocks'])
    
    def test_block_detail_view_with_authenticated_user_GET(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url_block_detail)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_block_detail)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEquals(response.context['block_mastery_level'], 0.5)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertFalse(response.context['learning_block'].is_completed)
    
    def test_block_detail_view_with_anonymous_user_GET(self):
        self.client.logout()
        response = self.client.get(self.url_block_detail)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_block_detail)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], int)
        self.assertEquals(response.context['block_mastery_level'], 0)
        self.assertFalse(response.context['learning_block'].is_completed)
    
    def test_block_detail_view_with_user_with_completed_block_GET(self):
        self.client.login(username='test_user_complete_block', password='test_password')
        response = self.client.get(self.url_block_detail)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_block_detail)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEquals(response.context['block_mastery_level'], 1.0)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertTrue(response.context['learning_block'].is_completed)
    
    def test_edit_blocks_view_as_unauthorized_user_GET(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url_blocks_table)
        
        self.assertEquals(response.status_code, 302)
    
    def test_edit_blocks_view_as_staff_GET(self):
        self.client.login(username='test_superuser', password='test_password')
        response = self.client.get(self.url_blocks_table)
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_blocks_table)
        self.assertIsNotNone(response.context['blocks'])
        self.assertIsInstance(response.context['blocks'], QuerySet)
        self.assertIn(self.test_block, response.context['blocks'])
    
    def test_edit_block_detail_view_as_unauthorized_user_GET(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url_block_edit)

        self.assertEquals(response.status_code, 302)
        self.assertTemplateUsed(self.template_name_block_edit)
    
    def test_edit_block_detail_view_as_staff_GET(self):
        self.client.login(username='test_superuser', password='test_password')
        response = self.client.get(self.url_block_edit)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(self.template_name_block_edit)
        self.assertIsInstance(response.context['block_words'], QuerySet)
        self.assertIn(self.test_word_info, response.context['block_words'])
    
    def test_add_word_info_view_GET(self):
        response = self.client.get(self.url_add_word_info)

        self.assertEquals(response.status_code, 405)
        
    def test_add_word_info_view_as_unauthorized_user_POST(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url_add_word_info, data={'learning_block_id': self.test_block.id})

        self.assertEquals(response.status_code, 302)
    
    def test_add_word_info_view_as_staff_POST(self):
        self.client.login(username='test_superuser', password='test_password')
        response = self.client.post(self.url_add_word_info, data={'learning_block_id': self.test_block.id})
        response_content = response.content.decode('utf-8')

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response_content, {'success': True})
    
    def test_edit_word_info_view_GET(self):
        response = self.client.get(self.url_edit_word_info)

        self.assertEquals(response.status_code, 405)
        
    def test_edit_word_info_view_as_unauthorized_user_POST(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url_edit_word_info, data={
            'word_id': self.test_word_info.id,
            'changed_field': 'translation',
            'new_value': 'New Translation'
        })

        self.assertEquals(response.status_code, 302)
    
    def test_edit_word_info_view_as_staff_POST(self):
        word_id = self.test_word_info.id
        self.client.login(username='test_superuser', password='test_password')
        changed_field = 'translation'
        old_value = self.test_word_info.translation
        new_value = 'New Translation'
        response = self.client.post(self.url_edit_word_info, data={
            'word_id': word_id,
            'changed_field': changed_field,
            'new_value': new_value
        })
        response_content = response.content.decode('utf-8')

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response_content, {
            'success': True,
            'word_id': str(word_id),
            'changed_field': changed_field, 
            'old_value': old_value,
            'new_value': new_value,
            'updated_at': self.test_word_info.updated_at.strftime('%H:%M:%S %d-%m-%Y')
        })
    
    def test_user_words_list_view_as_anonymous_user_GET(self):
        self.client.logout()
        response = self.client.get(self.url_user_words)

        self.assertEqual(response.status_code, 302)
    
    def test_user_words_list_view_as_authenticated_user_GET(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url_user_words)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_user_words)
        self.assertIsInstance(response.context['words'], QuerySet)
        self.assertIn(self.test_user_word, response.context['words'])
        
    def test_user_block_detail_view_GET(self):
        response = self.client.get(self.url_user_block_detail)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.template_name_user_block_detail)
    
    def test_about_view_GET(self):
        response = self.client.get(self.url_about)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(self.template_name_about)
    
    def test_reset_test_block_GET(self):
        response = self.client.get(self.url_reset_test_block)

        self.assertEquals(response.status_code, 405)
        self.assertTemplateUsed(self.template_name_reset_test_block)
    
    def test_reset_test_block_as_unauthorized_user_POST(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url_reset_test_block)

        self.assertEquals(response.status_code, 302)
    
    def test_reset_test_block_as_superuser_POST(self):
        self.client.login(username='test_superuser', password='test_password')
        response = self.client.post(self.url_reset_test_block)
        response_content = response.content.decode('utf-8')

        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response_content, {'success': True})
    