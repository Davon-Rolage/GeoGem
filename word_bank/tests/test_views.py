from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.query import QuerySet
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import MyProfile
from word_bank.models import Block, UserWord, WordInfo


class LearnListViewTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('learn')
        self.template_name = 'word_bank/learn.html'
        self.test_block = Block.objects.create(name='Test Block')

    def test_learn_list_view_as_anonymous_user(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn(self.test_block, response.context['learning_blocks'])

    def test_learn_list_view_as_authenticated_user_GET(self):
        test_user = self.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        test_user_profile = test_user.profile
        test_user_profile.experience = 20
        test_user_profile.save()
        
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url)
        
        test_user_profile.refresh_from_db(fields=['experience'])
        
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(test_user_profile.experience, 20)
        self.assertEqual(test_user_profile.level, 2)
        self.assertIn(self.test_block, response.context['learning_blocks'])
        

class BlockDetailViewTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('block_detail', args=['test-block'])
        self.template_name = 'word_bank/block_detail.html'

        self.test_block = Block.objects.create(name='Test Block')
        for i in range(2):
            word_info = WordInfo.objects.create(name=f'Test Word {i}')
            word_info.blocks.add(self.test_block)

        self.test_word_info, self.test_word_info2 = WordInfo.objects.all()
        
    def test_block_detail_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], int)
        self.assertEqual(response.context['block_mastery_level'], 0)
        self.assertFalse(response.context['learning_block'].is_completed)

    def test_block_detail_view_as_authenticated_user_GET(self):
        test_user = self.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        UserWord.objects.create(word=self.test_word_info, user=test_user, points=1)
        
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url)

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEqual(response.context['block_mastery_level'], 0.5)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertFalse(response.context['learning_block'].is_completed)
    
    def test_block_detail_view_as_user_with_completed_block_GET(self):
        test_user_complete_block = self.User.objects.create_user(
            username='test_user_complete_block', password='test_password', is_active=True
        )
        UserWord.objects.bulk_create([
            UserWord(word=word, user=test_user_complete_block, points=1) for word in WordInfo.objects.all()
        ])
        
        login = self.client.login(username='test_user_complete_block', password='test_password')
        response = self.client.get(self.url)

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEqual(response.context['block_mastery_level'], 1.0)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertTrue(response.context['learning_block'].is_completed)


class EditBlocksViewTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('blocks_table')
        self.template_name = 'word_bank/blocks_table.html'

        test_blocks = [
            Block(name=f'Test Block {i}') for i in range(1, 3)
        ]
        Block.objects.bulk_create(test_blocks)
        self.test_block, self.test_block2 = test_blocks

        test_word_infos = [
            WordInfo(name=f'Test Word {i}') for i in range(2)
        ]
        WordInfo.objects.bulk_create(test_word_infos)
        self.test_word_info, self.test_word_info2 = test_word_infos
        for word in WordInfo.objects.all():
            word.blocks.add(self.test_block)

    def test_edit_blocks_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)

    def test_edit_blocks_view_as_unauthorized_user_GET(self):
        self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_edit_blocks_view_as_staff_GET(self):
        self.User.objects.create_user(
            username='test_user_staff', password='test_password', is_active=True, is_staff=True
        )
        login = self.client.login(username='test_user_staff', password='test_password')
        response = self.client.get(self.url)
        
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['blocks'])
        self.assertIsInstance(response.context['blocks'], QuerySet)
        self.assertIn(self.test_block, response.context['blocks'])
    

class EditBlockDetailViewTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('block_edit', args=['test-block'])
        self.template_name = 'word_bank/block_edit.html'

    def test_edit_block_detail_view_as_unauthorized_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_edit_block_detail_view_as_staff_GET(self):
        self.User.objects.create_user(
            username='test_user_staff', password='test_password', is_active=True, is_staff=True
        )
        test_block = Block.objects.create(name='Test Block')
        test_word_info = WordInfo.objects.create(name='Test Word')
        test_word_info.blocks.add(test_block)
        
        login = self.client.login(username='test_user_staff', password='test_password')
        response = self.client.get(self.url)

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsInstance(response.context['block_words'], QuerySet)
        self.assertIn(test_word_info, response.context['block_words'])


class AddWordInfoViewTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('add_word_info')
        self.test_block = Block.objects.create(name='Test Block')
        self.request_data = {'learning_block_id': self.test_block.id}
    
    def test_add_word_info_view_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
    
    def test_add_word_info_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, data=self.request_data)

        self.assertEqual(response.status_code, 302)
        
    def test_add_word_info_view_as_unauthorized_user_POST(self):
        self.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url, data=self.request_data)

        self.assertTrue(login)
        self.assertEqual(response.status_code, 302)
    
    def test_add_word_info_view_as_staff_POST(self):
        self.User.objects.create_user(
            username='test_user_staff', password='test_password', is_active=True, is_staff=True
        )
        login = self.client.login(username='test_user_staff', password='test_password')
        response = self.client.post(self.url, data=self.request_data)
        response_content = response.content.decode('utf-8')

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {'success': True})


class EditWordInfoViewTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('edit_word_info')
        self.test_block = Block.objects.create(name='Test Block')
        self.test_word_info = WordInfo.objects.create(name='Test Word')
        self.test_word_info.blocks.add(self.test_block)
        self.request_data = {
            'word_id': self.test_word_info.id,
            'changed_field': 'translation',
            'new_value': 'New Translation'
        }

    def test_edit_word_info_view_method_not_allowed_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        
    def test_edit_word_info_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, data=self.request_data)
        self.assertEqual(response.status_code, 302)
        
    def test_edit_word_info_view_as_unauthorized_user_POST(self):
        self.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url, data=self.request_data)

        self.assertTrue(login)
        self.assertEqual(response.status_code, 302)
    
    def test_edit_word_info_view_as_staff_POST(self):
        self.User.objects.create_user(
            username='test_user_staff', password='test_password', is_active=True, is_staff=True
        )
        login = self.client.login(username='test_user_staff', password='test_password')
        old_value = self.test_word_info.translation

        response = self.client.post(self.url, data=self.request_data)
        response_content = response.content.decode('utf-8')

        self.assertTrue(login)
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

    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('user_words')
        self.template_name = 'word_bank/user_words.html'

    def test_user_words_list_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_user_words_list_view_as_authenticated_user_GET(self):
        test_user = self.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        word_info = WordInfo.objects.create(name='Test Word')
        test_user_word = UserWord.objects.create(user=test_user, word=word_info)

        login = self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url)
        response_words = response.context['words']

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsInstance(response_words, QuerySet)
        self.assertIn(test_user_word, response_words)


class UserBlockDetailViewTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.test_block = Block.objects.create(name='Test Block')
        self.url = reverse('user_block_detail', args=['test-block'])
        self.template_name = 'word_bank/user_block_detail.html'

    def test_user_block_detail_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(len(response.context['words']), 0)

    def test_user_block_detail_view_as_authenticated_user_GET(self):
        for i in range(2):
            word_info = WordInfo.objects.create(name=f'Test Word {i}')
            word_info.blocks.add(self.test_block)
            
        test_user = self.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        UserWord.objects.bulk_create([
            UserWord(user=test_user, word=word_info) for word_info in WordInfo.objects.all()
        ])
        test_user_word_count = UserWord.objects.filter(user=test_user).count()

        login = self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url)
        response_words = response.context['words']

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsInstance(response_words, QuerySet)
        self.assertEqual(len(response_words), test_user_word_count)
        
    def test_user_block_detail_view_method_not_allowed(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)


class AboutViewTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('about')
        self.template_name = 'word_bank/about.html'
    
    def test_about_view_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.template_name)
    
    def test_about_view_method_not_allowed(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(self.template_name)


class ResetTestBlockViewTestCase(TestCase):
    
    def setUp(self):
        self.User = get_user_model()
        self.client = Client()
        self.url = reverse('reset_test_block')
    
    def test_reset_test_block_view_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
    
    def test_reset_test_block_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
    
    def test_reset_test_block_view_as_unauthorized_user_POST(self):
        self.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url)

        self.assertTrue(login)
        self.assertEqual(response.status_code, 302)
    
    def test_reset_test_block_view_as_staff_POST(self):
        self.User.objects.create_user(
            username='test_user_staff', password='test_password', is_active=True, is_staff=True
        )
        login = self.client.login(username='test_user_staff', password='test_password')
        response = self.client.post(self.url)
        response_content = response.content.decode('utf-8')

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {'success': True})
    