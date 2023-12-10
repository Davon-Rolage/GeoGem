from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.test import Client, TestCase
from django.urls import reverse

from word_bank.models import Block, UserWord, WordInfo


class LearnListViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('learn')
        cls.template_name = 'word_bank/learn.html'
        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )

    def test_learn_list_view_as_anonymous_user(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIn(self.test_block, response.context['learning_blocks'])

    def test_learn_list_view_as_authenticated_user_GET(self):
        test_user_profile = self.test_user.profile
        test_user_profile.experience = 20
        test_user_profile.save()
        
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)
        
        test_user_profile.refresh_from_db(fields=['experience'])
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(test_user_profile.experience, 20)
        self.assertEqual(test_user_profile.level, 2)
        self.assertIn(self.test_block, response.context['learning_blocks'])
        

class BlockDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('block_detail', args=['test-block'])
        cls.template_name = 'word_bank/block_detail.html'

        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_complete_block = cls.User.objects.create_user(
            username='test_user_complete_block', password='test_password', is_active=True
        )
        for i in range(2):
            word_info = WordInfo.objects.create(name=f'Test Word {i}')
            word_info.blocks.add(cls.test_block)

        cls.test_word_info, cls.test_word_info2 = WordInfo.objects.all()
        
    def test_block_detail_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], int)
        self.assertEqual(response.context['block_mastery_level'], 0)
        self.assertFalse(response.context['learning_block'].is_completed)

    def test_block_detail_view_as_authenticated_user_GET(self):
        UserWord.objects.create(word=self.test_word_info, user=self.test_user, points=1)
        
        self.client.force_login(self.test_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(response.context['block_words'])
        self.assertIsInstance(response.context['block_mastery_level'], float)
        self.assertEqual(response.context['block_mastery_level'], 0.5)
        self.assertGreaterEqual(response.context['num_learned_words'], 0)
        self.assertIsInstance(response.context['ml_chart'], dict)
        self.assertFalse(response.context['learning_block'].is_completed)
    
    def test_block_detail_view_as_user_with_completed_block_GET(self):
        UserWord.objects.bulk_create([
            UserWord(word=word, user=self.test_user_complete_block, points=1) for word in WordInfo.objects.all()
        ])
        self.client.force_login(self.test_user_complete_block)
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
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('blocks_table')
        cls.template_name = 'word_bank/blocks_table.html'

        test_blocks = [
            Block(name=f'Test Block {i}') for i in range(1, 3)
        ]
        Block.objects.bulk_create(test_blocks)
        cls.test_block, cls.test_block2 = test_blocks
        
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_staff = cls.User.objects.create_user(
            username='test_user_staff', password='test_password', is_active=True, is_staff=True
        )
        
        for i in range(2):
            word_info = WordInfo.objects.create(name=f'Test Word {i}')
            word_info.blocks.add(cls.test_block)
            
        cls.test_word_info, cls.test_word_info2 = WordInfo.objects.all()
            

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
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('block_edit', args=['test-block'])
        cls.template_name = 'word_bank/block_edit.html'

        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_word_info = WordInfo.objects.create(name='Test Word')
        cls.test_word_info.blocks.add(cls.test_block)
        
        cls.test_user_staff = cls.User.objects.create_user(
            username='test_user_staff', password='test_password',
            is_active=True, is_staff=True
        )

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
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('add_word_info')
        cls.test_block = Block.objects.create(name='Test Block')
        cls.request_data = {'learning_block_id': cls.test_block.id}

        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_staff = cls.User.objects.create_user(
            username='test_user_staff', password='test_password',
            is_active=True, is_staff=True
        )
    
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
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('edit_word_info')

        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_word_info = WordInfo.objects.create(name='Test Word')
        cls.test_word_info.blocks.add(cls.test_block)
        cls.request_data = {
            'word_id': cls.test_word_info.id,
            'changed_field': 'translation',
            'new_value': 'New Translation'
        }
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_staff = cls.User.objects.create_user(
            username='test_user_staff', password='test_password',
            is_active=True, is_staff=True
        )

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
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('user_words')
        cls.template_name = 'word_bank/user_words.html'

        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )

    def test_user_words_list_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_user_words_list_view_as_authenticated_user_GET(self):
        
        word_info = WordInfo.objects.create(name='Test Word')
        test_user_word = UserWord.objects.create(user=self.test_user, word=word_info)

        self.client.force_login(self.test_user)
        response = self.client.get(self.url)
        response_words = response.context['words']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsInstance(response_words, QuerySet)
        self.assertIn(test_user_word, response_words)


class UserBlockDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('user_block_detail', args=['test-block'])
        cls.template_name = 'word_bank/user_block_detail.html'

        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        for i in range(2):
            word_info = WordInfo.objects.create(name=f'Test Word {i}')
            word_info.blocks.add(cls.test_block)

    def test_user_block_detail_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(len(response.context['words']), 0)

    def test_user_block_detail_view_as_authenticated_user_GET(self):
        UserWord.objects.bulk_create([
            UserWord(user=self.test_user, word=word_info) for word_info in WordInfo.objects.all()
        ])
        test_user_word_count = UserWord.objects.filter(user=self.test_user).count()

        self.client.force_login(self.test_user)
        response = self.client.get(self.url)
        response_words = response.context['words']

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsInstance(response_words, QuerySet)
        self.assertEqual(len(response_words), test_user_word_count)
        
    def test_user_block_detail_view_method_not_allowed_POST(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)


class AboutViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
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
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('reset_test_block')

        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_staff = cls.User.objects.create_user(
            username='test_user_staff', password='test_password',
            is_active=True, is_staff=True
        )
    
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
    