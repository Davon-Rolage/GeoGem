from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from word_bank.models import Block, WordInfo, UserWord


class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.test_user = get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        self.test_user_newbie = get_user_model().objects.create_user(
            username='test_user_newbie', password='test_password', is_active=True
        )
        self.client.login(username='test_user', password='test_password')
        self.test_block = Block.objects.create(
            name='Test Block', description='test-block description'
        )
        for i in range(10):
            word = WordInfo.objects.create(
                name=f'Test Word {i+1}', translation=f'Test Word {i+1} Translation'
            )
            word.blocks.add(self.test_block)
            UserWord.objects.create(user=self.test_user, word=word, points=1)
        
        self.test_block_num_words = self.test_block.wordinfo_set.count()
        self.test_word_info = WordInfo.objects.first()
        
        self.url_quiz_multiple_choice = reverse('quiz_multiple_choice')
        self.url_quiz_learn = reverse('quiz_learn')
        self.url_quiz_review = reverse('quiz_review')
        self.url_quiz_results = reverse('quiz_results')
        
        self.template_name_quiz_multiple_choice = 'quizzer/quiz_multiple_choice.html'
        self.template_name_quiz_learn = 'quizzer/quiz_learn.html'
        self.template_name_quiz_review = 'quizzer/quiz_review.html'
        self.template_name_quiz_results = 'quizzer/quiz_results.html'
        
    def test_quiz_multiple_choice_view_GET(self):
        response = self.client.get(self.url_quiz_multiple_choice)

        self.assertEquals(response.status_code, 405)
    
    def test_quiz_multiple_choice_view_POST(self):
        response = self.client.post(self.url_quiz_multiple_choice, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_quiz_multiple_choice)

    
    def test_quiz_learn_view_GET(self):
        response = self.client.get(self.url_quiz_learn, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 405)
    
    def test_quiz_learn_view_all_words_learned_as_authenticated_user_POST(self):
        response = self.client.post(self.url_quiz_learn, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_quiz_learn)
        self.assertEquals(response.context['learning_block'].slug, 'test-block')
        self.assertEqual(len(response.context['words']), 0)
        
    def test_quiz_learn_view_has_words_to_learn_as_authenticated_user_POST(self):
        self.client.login(username='test_user_newbie', password='test_password')
        response = self.client.post(self.url_quiz_learn, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_quiz_learn)
        self.assertEquals(response.context['learning_block'].slug, 'test-block')
        self.assertGreater(len(response.context['words']), 0)
        
    def test_quiz_learn_view_as_anonymous_user_POST(self):
        self.client.logout()
        response = self.client.post(self.url_quiz_learn, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_quiz_learn)
        self.assertEquals(response.context['learning_block'].slug, 'test-block')
        self.assertEquals(len(response.context['words']), self.test_block_num_words)
        
    
    def test_quiz_review_view_as_authenticated_user_GET(self):
        response = self.client.get(self.url_quiz_review, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 405)
        
    def test_quiz_review_view_as_anonymous_user_GET(self):
        self.client.logout()
        response = self.client.get(self.url_quiz_review, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 302)
    
    def test_quiz_review_view_as_anonymous_user_POST(self):
        self.client.logout()
        response = self.client.post(self.url_quiz_review, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 302)

    def test_quiz_review_view_as_authenticated_user_POST(self):
        response = self.client.post(self.url_quiz_review, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_quiz_review)
    

    def test_quiz_results_view_GET(self):
        response = self.client.get(self.url_quiz_results, data={'learning_block': 'test-block'})
        
        self.assertEquals(response.status_code, 405)
        
    def test_quiz_results_view_as_anonymous_user_POST(self):
        self.client.logout()
        response = self.client.post(self.url_quiz_results, data={
            'learning_block': 'test-block',
            'quiz_words': str(self.test_word_info.id),
            'quiz_type': 'learn',
            'quiz_score': 0
        })
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_quiz_results)
    
    def test_quiz_results_view_as_authenticated_user_POST(self):
        user_word = UserWord.objects.get(user=self.test_user, word=self.test_word_info)
        response = self.client.post(self.url_quiz_results, data={
            'learning_block': 'test-block',
            'quiz_words': str(user_word.id),
            'quiz_type': 'learn',
            'quiz_score': 0
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name_quiz_results)
    