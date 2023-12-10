from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse

from word_bank.models import Block, UserWord, WordInfo


class QuizMultipleChoiceViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.client = Client()

        cls.url = reverse('quiz_multiple_choice')
        cls.template_name = 'quizzer/quiz_multiple_choice.html'
        cls.request_data = {'learning_block': 'test-block'}
        
        test_password = make_password('test_password')
        test_users = [
            User(username='test_user', password=test_password, is_active=True),
            User(username='test_user_newbie', password=test_password, is_active=True),
        ]
        User.objects.bulk_create(test_users)
        cls.test_user, cls.test_user_newbie = test_users

        cls.test_block = Block.objects.create(name='Test Block')

        for i in range(10):
            word = WordInfo.objects.create(
                name=f'Test Word {i+1}', translation=f'Test Word {i+1} Translation'
            )
            word.blocks.add(cls.test_block)
            UserWord.objects.create(user=cls.test_user, word=word, points=1)
        
        cls.test_block_num_words = cls.test_block.wordinfo_set.count()
        cls.test_word_info = WordInfo.objects.first()
        
    def test_quiz_multiple_choice_view_method_not_allowed_GET(self):
        response = self.client.get(self.url, data=self.request_data)

        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_quiz_multiple_choice_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, data=self.request_data)
        words = response.context['words']
        num_words = len(words)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(words)
        self.assertIsInstance(words, list)
        self.assertEqual(num_words, self.test_block_num_words)
        
    def test_quiz_multiple_choice_view_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, data=self.request_data)
        words = response.context['words']
        num_words = len(words)
     
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(words)
        self.assertIsInstance(words, list)
        self.assertEqual(num_words, self.test_block_num_words)


class QuizLearnViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.client = Client()

        cls.url = reverse('quiz_learn')
        cls.template_name = 'quizzer/quiz_learn.html'
        cls.request_data = {'learning_block': 'test-block'}

        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_word_info = WordInfo.objects.create()
        cls.test_word_info.blocks.add(cls.test_block)
        cls.test_block_num_words = cls.test_block.wordinfo_set.count()
        
        test_password = make_password('test_password')
        cls.test_user = User.objects.create(username='test_user', password=test_password, is_active=True)
        cls.test_user_newbie = User.objects.create(username='test_user_newbie', password=test_password, is_active=True)
        
        cls.test_user_word = UserWord.objects.create(user=cls.test_user, word=cls.test_word_info, points=1)
        
    def test_quiz_learn_view_GET(self):
        response = self.client.get(self.url, data=self.request_data)
        
        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_quiz_learn_view_all_words_learned_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, data=self.request_data)
        num_words = len(response.context['words'])
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(response.context['learning_block'].slug, 'test-block')
        self.assertEqual(num_words, 0)
        
    def test_quiz_learn_view_has_words_to_learn_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user_newbie)
        response = self.client.post(self.url, data=self.request_data)
        num_words = len(response.context['words'])
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(response.context['learning_block'].slug, 'test-block')
        self.assertGreater(num_words, 0)
        
    def test_quiz_learn_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, data=self.request_data)
        num_words = len(response.context['words'])
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(response.context['learning_block'].slug, 'test-block')
        self.assertEqual(num_words, self.test_block_num_words)
        

class QuizReviewViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.client = Client()
        
        cls.url = reverse('quiz_review')
        cls.template_name = 'quizzer/quiz_review.html'
        cls.request_data = {'learning_block': 'test-block'}

        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_word_info = WordInfo.objects.create(name='Test Word')
        cls.test_word_info.blocks.add(cls.test_block)
        cls.test_user = User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_word = UserWord.objects.create(user=cls.test_user, word=cls.test_word_info, points=2)

    def test_quiz_review_view_as_authenticated_user_GET(self):
        self.client.force_login(self.test_user)
        response = self.client.get(self.url, data=self.request_data)
        
        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(response, self.template_name)
        
    def test_quiz_review_view_as_anonymous_user_GET(self):
        response = self.client.get(self.url, data=self.request_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_quiz_review_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, data=self.request_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, self.template_name)

    def test_quiz_review_view_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, data=self.request_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)


class QuizResultsViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.client = Client()
        
        cls.url = reverse('quiz_results')
        cls.template_name = 'quizzer/quiz_results.html'
        cls.request_data = {
            'learning_block': 'test-block',
            'quiz_words': '',
            'quiz_type': 'learn',
            'quiz_score': 0
        }
        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_word_info = WordInfo.objects.create()
        cls.test_user = User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_word = UserWord.objects.create(
            user=cls.test_user, word=cls.test_word_info
        )

    def test_quiz_results_view_method_not_allowed_GET(self):
        response = self.client.get(self.url, data=self.request_data)

        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(response, self.template_name)
        
    def test_quiz_results_view_as_anonymous_user_POST(self):
        request_data = self.request_data
        request_data['quiz_words'] = str(self.test_word_info.id)

        response = self.client.post(self.url, data=request_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
    
    def test_quiz_results_view_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user)
        request_data = self.request_data
        request_data['quiz_words'] = str(self.test_user_word.id)
        
        response = self.client.post(self.url, data=request_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
    