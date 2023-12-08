from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse

from word_bank.models import Block, UserWord, WordInfo


class QuizMultipleChoiceViewTestCase(TestCase):
    
    def setUp(self):
        User = get_user_model()
        self.client = Client()

        self.url = reverse('quiz_multiple_choice')
        self.template_name = 'quizzer/quiz_multiple_choice.html'
        self.request_data = {'learning_block': 'test-block'}
        
        test_password = make_password('test_password')
        test_users = [
            User(username='test_user', password=test_password, is_active=True),
            User(username='test_user_newbie', password=test_password, is_active=True),
        ]
        User.objects.bulk_create(test_users)
        self.test_user, self.test_user_newbie = test_users

        self.test_block = Block.objects.create(name='Test Block')

        for i in range(10):
            word = WordInfo.objects.create(
                name=f'Test Word {i+1}', translation=f'Test Word {i+1} Translation'
            )
            word.blocks.add(self.test_block)
            UserWord.objects.create(user=self.test_user, word=word, points=1)
        
        self.test_block_num_words = self.test_block.wordinfo_set.count()
        self.test_word_info = WordInfo.objects.first()
        
    def test_quiz_multiple_choice_view_GET(self):
        response = self.client.get(self.url, data=self.request_data)

        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_quiz_multiple_choice_view_as_authenticated_user_POST(self):
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url, data=self.request_data)
        words = response.context['words']
        num_words = len(words)
     
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(words)
        self.assertIsInstance(words, list)
        self.assertEqual(num_words, self.test_block_num_words)
    
    def test_quiz_multiple_choice_view_as_anonymous_user_POST(self):
        response = self.client.post(self.url, data=self.request_data)
        words = response.context['words']
        num_words = len(words)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertIsNotNone(words)
        self.assertIsInstance(words, list)
        self.assertEqual(num_words, self.test_block_num_words)


class QuizLearnViewTestCase(TestCase):
    
    def setUp(self):
        User = get_user_model()
        self.client = Client()

        self.url = reverse('quiz_learn')
        self.template_name = 'quizzer/quiz_learn.html'
        self.request_data = {'learning_block': 'test-block'}

        self.test_block = Block.objects.create(name='Test Block')
        self.test_word_info = WordInfo.objects.create()
        self.test_word_info.blocks.add(self.test_block)
        self.test_block_num_words = self.test_block.wordinfo_set.count()
        
        test_password = make_password('test_password')
        test_users = [
            User(username='test_user', password=test_password, is_active=True),
            User(username='test_user_newbie', password=test_password, is_active=True),
        ]
        User.objects.bulk_create(test_users)
        self.test_user, self.test_user_newbie = test_users
        
        self.test_user_word = UserWord.objects.create(user=self.test_user, word=self.test_word_info, points=1)
        
    def test_quiz_learn_view_GET(self):
        response = self.client.get(self.url, data=self.request_data)
        
        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_quiz_learn_view_all_words_learned_as_authenticated_user_POST(self):
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url, data=self.request_data)
        num_words = len(response.context['words'])
        
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(response.context['learning_block'].slug, 'test-block')
        self.assertEqual(num_words, 0)
        
    def test_quiz_learn_view_has_words_to_learn_as_authenticated_user_POST(self):
        login = self.client.login(username='test_user_newbie', password='test_password')
        response = self.client.post(self.url, data=self.request_data)
        num_words = len(response.context['words'])
        
        self.assertTrue(login)
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
    
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        
        self.url = reverse('quiz_review')
        self.template_name = 'quizzer/quiz_review.html'
        self.request_data = {'learning_block': 'test-block'}
        self.test_block = Block.objects.create(name='Test Block')
        self.test_word_info = WordInfo.objects.create(name='Test Word')
        self.test_word_info.blocks.add(self.test_block)
        self.test_user = User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        self.test_user_word = UserWord.objects.create(user=self.test_user, word=self.test_word_info, points=2)

    def test_quiz_review_view_as_authenticated_user_GET(self):
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.get(self.url, data=self.request_data)
        
        self.assertTrue(login)
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
        login = self.client.login(username='test_user', password='test_password')
        template_name = 'quizzer/quiz_review.html'
        response = self.client.post(self.url, data=self.request_data)
        
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)


class QuizResultsViewTestCase(TestCase):
    
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        
        self.url = reverse('quiz_results')
        self.template_name = 'quizzer/quiz_results.html'
        self.test_block = Block.objects.create(name='Test Block')
        self.test_word_info = WordInfo.objects.create()
        self.test_user = User.objects.create_user(username='test_user', password='test_password', is_active=True)

    def test_quiz_results_view_GET(self):
        response = self.client.get(self.url, data={'learning_block': 'test-block'})
        
        self.assertEqual(response.status_code, 405)
        
    def test_quiz_results_view_as_anonymous_user_POST(self):        
        response = self.client.post(self.url, data={
            'learning_block': 'test-block',
            'quiz_words': str(self.test_word_info.id),
            'quiz_type': 'learn',
            'quiz_score': 0
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
    
    def test_quiz_results_view_as_authenticated_user_POST(self):
        login = self.client.login(username='test_user', password='test_password')
        user_word = UserWord.objects.create(user=self.test_user, word=self.test_word_info)

        response = self.client.post(self.url, data={
            'learning_block': 'test-block',
            'quiz_words': str(user_word.id),
            'quiz_type': 'learn',
            'quiz_score': 0
        })
        
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
    