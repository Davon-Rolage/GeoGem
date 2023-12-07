from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import MyProfile
from word_bank.models import Block, UserWord, WordInfo


class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.test_block = Block.objects.create(name='Test Block')
        self.test_word_info = WordInfo.objects.create(name='Test Word', translation='Test Word Translation')
        self.test_word_info2 = WordInfo.objects.create(name='Test Word 2', translation='Test Word 2 Translation')
        
        self.test_block.wordinfo_set.add(*WordInfo.objects.all())
        
        self.test_user = get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        self.client.login(username='test_user', password='test_password')
        self.test_superuser = get_user_model().objects.create_superuser(
            username='test_superuser', password='test_password', is_active=True
        )

        self.test_profile = MyProfile.objects.create(user=self.test_user, experience=20)
        self.test_user_word = UserWord.objects.create(user=self.test_user, word=self.test_word_info, points=1)

        self.test_user_complete_block = get_user_model().objects.create_user(
            username='test_user_complete_block', password='test_password', is_active=True
        )
        
        UserWord.objects.bulk_create([
            UserWord(user=self.test_user_complete_block, word=word_info, points=1) for word_info in WordInfo.objects.all()
        ])

    def test_learn_list_view_with_authenticated_user_GET(self):
        url = reverse('learn')
        template_name = 'word_bank/learn.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertEqual(response.context['user'].experience, 20)
        self.assertEqual(response.context['user'].level, 2)
        self.assertIn(self.test_block, response.context['learning_blocks'])
        
    def test_learn_list_view_with_anonymous_user(self):
        self.client.logout()
        url = reverse('learn')
        template_name = 'word_bank/learn.html'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertEqual(response.context['user'].experience, 0)
        self.assertEqual(response.context['user'].level, 0)
        self.assertIn(self.test_block, response.context['learning_blocks'])
    
    def test_block_detail_view_with_authenticated_user_GET(self):
        url = reverse('block_detail', args=['test-block'])
        template_name = 'word_bank/block_detail.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEqual(response.context['block_mastery_level'], 0.5)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertFalse(response.context['learning_block'].is_completed)
    
    def test_block_detail_view_with_anonymous_user_GET(self):
        self.client.logout()
        url = reverse('block_detail', args=['test-block'])
        template_name = 'word_bank/block_detail.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], int)
        self.assertEqual(response.context['block_mastery_level'], 0)
        self.assertFalse(response.context['learning_block'].is_completed)
    
    def test_block_detail_view_with_user_with_completed_block_GET(self):
        self.client.login(username='test_user_complete_block', password='test_password')
        url = reverse('block_detail', args=['test-block'])
        template_name = 'word_bank/block_detail.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEqual(response.context['block_mastery_level'], 1.0)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertTrue(response.context['learning_block'].is_completed)
    
    def test_edit_blocks_view_as_unauthorized_user_GET(self):
        url = reverse('blocks_table')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
    
    def test_edit_blocks_view_as_staff_GET(self):
        self.client.login(username='test_superuser', password='test_password')
        url = reverse('blocks_table')
        template_name = 'word_bank/blocks_table.html'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsNotNone(response.context['blocks'])
        self.assertIsInstance(response.context['blocks'], QuerySet)
        self.assertIn(self.test_block, response.context['blocks'])
    
    def test_edit_block_detail_view_as_unauthorized_user_GET(self):
        url = reverse('block_edit', args=['test-block'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
    
    def test_edit_block_detail_view_as_staff_GET(self):
        self.client.login(username='test_superuser', password='test_password')
        url = reverse('block_edit', args=['test-block'])
        template_name = 'word_bank/block_edit.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context['block_words'], QuerySet)
        self.assertIn(self.test_word_info, response.context['block_words'])
    
    def test_add_word_info_view_GET(self):
        url = reverse('add_word_info')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)
        
    def test_add_word_info_view_as_unauthorized_user_POST(self):
        url = reverse('add_word_info')
        response = self.client.post(url, data={'learning_block_id': self.test_block.id})

        self.assertEqual(response.status_code, 302)
    
    def test_add_word_info_view_as_staff_POST(self):
        self.client.login(username='test_superuser', password='test_password')
        url = reverse('add_word_info')
        response = self.client.post(url, data={'learning_block_id': self.test_block.id})
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {'success': True})
    
    def test_edit_word_info_view_GET(self):
        url = reverse('edit_word_info')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)
        
    def test_edit_word_info_view_as_unauthorized_user_POST(self):
        url = reverse('edit_word_info')
        response = self.client.post(url, data={
            'word_id': self.test_word_info.id,
            'changed_field': 'translation',
            'new_value': 'New Translation'
        })

        self.assertEqual(response.status_code, 302)
    
    def test_edit_word_info_view_as_staff_POST(self):
        self.client.login(username='test_superuser', password='test_password')

        word_id = self.test_word_info.id
        changed_field = 'translation'
        old_value = self.test_word_info.translation
        new_value = 'New Translation'
        
        url = reverse('edit_word_info')
        response = self.client.post(url, data={
            'word_id': word_id,
            'changed_field': changed_field,
            'new_value': new_value
        })
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
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
        url = reverse('user_words')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
    
    def test_user_words_list_view_as_authenticated_user_GET(self):
        url = reverse('user_words')
        template_name = 'word_bank/user_words.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertIsInstance(response.context['words'], QuerySet)
        self.assertIn(self.test_user_word, response.context['words'])
        
    def test_user_block_detail_view_GET(self):
        url = reverse('user_block_detail', args=['test-block'])
        template_name = 'word_bank/user_block_detail.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
    
    def test_about_view_GET(self):
        url = reverse('about')
        template_name = 'word_bank/about.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name)
    
    def test_reset_test_block_GET(self):
        url = reverse('reset_test_block')
        template_name = 'word_bank/reset_test_block.html'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)
        self.assertTemplateUsed(template_name)
    
    def test_reset_test_block_as_unauthorized_user_POST(self):
        url = reverse('reset_test_block')
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
    
    def test_reset_test_block_as_superuser_POST(self):
        self.client.login(username='test_superuser', password='test_password')
        url = reverse('reset_test_block')
        response = self.client.post(url)
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {'success': True})
    