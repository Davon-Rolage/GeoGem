from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from word_bank.models import Block, UserWord, WordInfo


class QuizMultipleChoiceViewTestCase(TestCase):
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()

        cls.url = reverse('quiz_multiple_choice')
        cls.template_name = 'quizzer/quiz_multiple_choice.html'
        cls.request_data = {'learning_block': 'test-block'}
        
        cls.test_block = Block.objects.first()
        cls.test_block_num_words = cls.test_block.wordinfo_set.count()
        cls.test_user = cls.User.objects.first()
        
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
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('quiz_learn')
        cls.template_name = 'quizzer/quiz_learn.html'
        cls.request_data = {'learning_block': 'test-block'}

        cls.test_block = Block.objects.first()
        cls.test_block_num_words = cls.test_block.wordinfo_set.count()
        
        test_users = cls.User.objects.all()
        cls.test_user_no_words = test_users.get(username='test_user_no_words')
        cls.test_user_all_words_learned = test_users.get(username='test_user_all_words_learned')
        
    def test_quiz_learn_view_GET(self):
        response = self.client.get(self.url, data=self.request_data)
        
        self.assertEqual(response.status_code, 405)
        self.assertTemplateNotUsed(response, self.template_name)
    
    def test_quiz_learn_view_all_words_learned_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user_all_words_learned)
        response = self.client.post(self.url, data=self.request_data)
        num_words = len(response.context['words'])
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(response.context['learning_block'].slug, 'test-block')
        self.assertEqual(num_words, 0)
        
    def test_quiz_learn_view_has_words_to_learn_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user_no_words)
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
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('quiz_review')
        cls.template_name = 'quizzer/quiz_review.html'

        cls.request_data = {'learning_block': 'test-block'}
        cls.test_user = cls.User.objects.first()

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
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.url = reverse('quiz_results')
        cls.template_name = 'quizzer/quiz_results.html'

        cls.request_data = {
            'learning_block': 'test-block',
            'quiz_words': '',
            'quiz_type': 'learn',
            'quiz_score': 0
        }
        cls.test_user = cls.User.objects.first()
        cls.test_word_info = WordInfo.objects.first()
        cls.test_user_word = UserWord.objects.first()

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
    