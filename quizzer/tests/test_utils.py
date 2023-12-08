from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse

from quizzer.utils import *
from word_bank.models import Block, UserWord, WordInfo


class UpdateUserWordPointsTestCase(TestCase):
    
    def setUp(self):
        self.test_user = get_user_model().objects.create_user(username='test_user', password='test_password', is_active=True)
        self.test_word_info = WordInfo.objects.create(name='test_name', translation='test')
        self.test_user_word = UserWord.objects.create(user=self.test_user, word=self.test_word_info, points=50)

    def test_update_user_word_points_correct_answer(self):
        is_correct = update_user_word_points('test', 'test', self.test_user_word)

        self.assertTrue(is_correct)
        self.assertEqual(self.test_user_word.points, 51)

    def test_update_user_word_points_incorrect_answer(self):
        is_correct = update_user_word_points('wrong', 'test', self.test_user_word)

        self.assertFalse(is_correct)
        self.assertEqual(self.test_user_word.points, 49)

    def test_update_user_word_points_increase_by_10(self):
        is_correct = update_user_word_points('test', 'test', self.test_user_word, increase_by=10)

        self.assertTrue(is_correct)
        self.assertEqual(self.test_user_word.points, 60)

    def test_update_user_word_points_decrease_by_10(self):
        is_correct = update_user_word_points('wrong', 'test', self.test_user_word, decrease_by=10)

        self.assertFalse(is_correct)
        self.assertEqual(self.test_user_word.points, 40)

    def test_update_user_word_points_no_change(self):
        is_correct = update_user_word_points('test', 'test', self.test_user_word, increase_by=0, decrease_by=0)

        self.assertTrue(is_correct)
        self.assertEqual(self.test_user_word.points, 50)
        
    def test_update_user_word_points_no_change_incorrect_answer(self):
        is_correct = update_user_word_points('wrong', 'test', self.test_user_word, increase_by=0, decrease_by=0)

        self.assertFalse(is_correct)
        self.assertEqual(self.test_user_word.points, 50)
    
    def test_update_user_word_points_overflow_100(self):
        is_correct = update_user_word_points('test', 'test', self.test_user_word, increase_by=101)

        self.assertTrue(is_correct)
        self.assertEqual(self.test_user_word.points, 100)

    def test_update_user_word_points_overflow_0(self):
        is_correct = update_user_word_points('wrong', 'test', self.test_user_word, decrease_by=101)
        
        self.assertFalse(is_correct)
        self.assertEqual(self.test_user_word.points, 0)


class UpdateProfileExperienceTestCase(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test_user', password='test_password', is_active=True)
        self.user_profile = self.user.profile
        self.user_profile.experience = 50
        self.user_profile.save()

    def test_update_profile_experience_as_authenticated_user(self):
        update_profile_experience(self.user)
        self.user_profile.refresh_from_db(fields=['experience'])
        
        self.assertEqual(self.user_profile.experience, 51)

    def test_update_profile_experience_increase_by_10(self):
        update_profile_experience(self.user, increase_by=10)
        self.user_profile.refresh_from_db(fields=['experience'])

        self.assertEqual(self.user_profile.experience, 60)


class AddToLearnedTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('add_to_learned')
        
        self.test_word_info = WordInfo.objects.create(name='test_name', translation='test')
        self.request_data = {'question_id': self.test_word_info.id, 'is_last': 'true'}

    def test_add_to_learned_as_anonymous_user_POST(self):
        response = self.client.post(self.url, self.request_data)
        response_content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {'is_last': True})
        
    def test_add_to_learned_as_authenticated_user_created_word_POST(self):
        test_user = get_user_model().objects.create_user(username='test_user', password='test_password', is_active=True)
        login = self.client.login(username='test_user', password='test_password')
        response = self.client.post(self.url, self.request_data)
        response_content = response.content.decode('utf-8')
        
        user_word = UserWord.objects.get(user=test_user, word=self.test_word_info)
        
        test_user_profile = test_user.profile
        test_user_profile.refresh_from_db(fields=['num_learned_words'])
        
        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_user_profile.num_learned_words, 1)
        self.assertEqual(user_word.points, 1)
        self.assertJSONEqual(response_content, {
            'is_last': True,
            'created': True,
            'user_word_id': user_word.id
        })
    
    def test_add_to_learned_as_authenticated_user_known_word_POST(self):
        test_user_with_words = get_user_model().objects.create_user(username='test_user_with_words', password='test_password', is_active=True)
        UserWord.objects.create(user=test_user_with_words, word=self.test_word_info, points=20)

        login = self.client.login(username='test_user_with_words', password='test_password')
        response = self.client.post(self.url, self.request_data)
        response_content = response.content.decode('utf-8')
        user_word = UserWord.objects.get(user=test_user_with_words, word=self.test_word_info)

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_word.points, 20)
        self.assertJSONEqual(response_content, {
            'is_last': True,
            'created': False,
            'user_word_id': user_word.id
        })


class CheckAnswerTestCase(TestCase):
    
    def setUp(self):
        self.url = reverse('check_answer')
        self.test_block = Block.objects.create(name='Test Block')
        self.test_word_info = WordInfo.objects.create(name='test_name', translation='test')
        self.test_word_info.blocks.add(self.test_block)

        self.test_user = get_user_model().objects.create_user(username='test_user', password='test_password', is_active=True)
        self.test_user_profile = self.test_user.profile
        self.test_user_profile.experience = 50
        self.test_user_profile.save()
        self.test_user_word = UserWord.objects.create(user=self.test_user, word=self.test_word_info, points=1)
    
    def test_check_answer_view_GET(self):
        response = self.client.get(self.url, {
            'quiz_type': 'learn',
            'question_id': 1,
            'answer': 'test',
        })

        self.assertEqual(response.status_code, 405)
    
    def test_check_answer_view_incorrect_quiz_type_POST(self):
        response = self.client.post(self.url, {
            'quiz_type': 'wrong_type',
            'question_id': 1,
            'answer': 'test',
        })

        self.assertEqual(response.status_code, 400)
    
    def test_check_answer_multiple_choice_correct_answer_as_anonymous_user_POST(self):
        response = self.client.post(self.url, {
            'quiz_type': 'multiple_choice',
            'question_id': self.test_word_info.id,
            'answer': 'test',
        })
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {
            'is_correct': True,
            'example_span': ''
        })
    
    def test_check_answer_multiple_choice_incorrect_answer_as_anonymous_user_POST(self):
        response = self.client.post(self.url, {
            'quiz_type': 'multiple_choice',
            'question_id': self.test_word_info.id,
            'answer': 'wrong',
        })
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {
            'is_correct': False,
            'example_span': ''
        })
    
    def test_check_answer_multiple_choice_correct_answer_as_authenticated_user_POST(self):
        login = self.client.login(username='test_user', password='test_password')
        profile_exp_before = self.test_user_profile.experience
        user_word_points_before = self.test_user_word.points
        
        response = self.client.post(self.url, {
            'quiz_type': 'multiple_choice',
            'question_id': self.test_word_info.id,
            'answer': 'test',
        })
        response_content = response.content.decode('utf-8')

        self.test_user_profile.refresh_from_db(fields=['experience'])
        self.test_user_word.refresh_from_db(fields=['points'])

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user_profile.experience - profile_exp_before, 2)
        self.assertEqual(self.test_user_word.points - user_word_points_before, 2)
        self.assertJSONEqual(response_content, {
            'is_correct': True,
            'example_span': ''
        })

    def test_check_answer_multiple_choice_incorrect_answer_as_authenticated_user_POST(self):
        login = self.client.login(username='test_user', password='test_password')
        profile_exp_before = self.test_user_profile.experience
        user_word_points_before = self.test_user_word.points
        
        response = self.client.post(self.url, {
            'quiz_type': 'multiple_choice',
            'question_id': self.test_word_info.id,
            'answer': 'wrong',
        })
        response_content = response.content.decode('utf-8')
        
        self.test_user_profile.refresh_from_db(fields=['experience'])
        self.test_user_word.refresh_from_db(fields=['points'])

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user_profile.experience, profile_exp_before)
        self.assertEqual(self.test_user_word.points - user_word_points_before, -1)
        self.assertJSONEqual(response_content, {
            'is_correct': False,
            'example_span': ''
        })
    
    
    def test_check_answer_review_correct_answer_as_authenticated_user_POST(self):
        login = self.client.login(username='test_user', password='test_password')
        profile_exp_before = self.test_user_profile.experience
        user_word_points_before = self.test_user_word.points
        
        response = self.client.post(self.url, {
            'quiz_type': 'review',
            'question_id': self.test_user_word.id,
            'answer': 'test',
        })
        response_content = response.content.decode('utf-8')

        self.test_user_profile.refresh_from_db(fields=['experience'])
        self.test_user_word.refresh_from_db(fields=['points'])

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user_profile.experience - profile_exp_before, 1)
        self.assertEqual(self.test_user_word.points - user_word_points_before, 1)
        
        self.assertJSONEqual(response_content, {
            'is_correct': True,
            'example_span': ''
        })
    
    def test_check_answer_review_incorrect_answer_as_authenticated_user_POST(self):
        login = self.client.login(username='test_user', password='test_password')
        profile_exp_before = self.test_user_profile.experience
        user_word_points_before = self.test_user_word.points
        
        response = self.client.post(self.url, {
            'quiz_type': 'review',
            'question_id': self.test_user_word.id,
            'answer': 'wrong',
        })
        response_content = response.content.decode('utf-8')

        self.test_user_profile.refresh_from_db(fields=['experience'])
        self.test_user_word.refresh_from_db(fields=['points'])

        self.assertTrue(login)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user_profile.experience, profile_exp_before)
        self.assertEqual(self.test_user_word.points - user_word_points_before, -1)
        
        self.assertJSONEqual(response_content, {
            'is_correct': False,
            'example_span': ''
        })


class PopulateExampleSpanTestCase(TestCase):
    
    def setUp(self):
        self.test_example_text = "example_text"
        self.test_example_image_url = "example_image_url"

    def test_populate_example_span_without_example(self):
        word = WordInfo()
        result = populate_example_span(word)
        self.assertEqual(result, "")
        
    def test_populate_example_span_with_example_text(self):
        word = WordInfo(example=self.test_example_text)
        result = populate_example_span(word)
        self.assertEqual(result, self.test_example_text)

    def test_populate_example_span_with_example_image(self):
        word = WordInfo(example_image=self.test_example_image_url)
        result = populate_example_span(word)
        self.assertIn("<img", result)
        self.assertIn(self.test_example_image_url, result)

    def test_populate_example_span_with_both_example_text_and_image(self):
        word = WordInfo(example=self.test_example_text, example_image=self.test_example_image_url)
        result = populate_example_span(word)
        self.assertIn("<img", result)
        self.assertIn(self.test_example_image_url, result)
        self.assertIn(self.test_example_text, result)


class ShuffleQuestionsOrderTestCase(TestCase):
    
    def setUp(self):
        self.questions = [x for x in range(1, 5)]

    def test_shuffle_questions_order_wrong_type(self):
        result = shuffle_questions_order(1)

        self.assertIsInstance(result, list)
        self.assertEqual(result, [])
    
    def test_shuffle_questions_order_empty_list(self):
        questions = []
        result = shuffle_questions_order(questions)

        self.assertIsInstance(result, list)
        self.assertEqual(result, questions)
    
    def test_shuffle_questions_order_none_list(self):
        questions = None
        result = shuffle_questions_order(questions)

        self.assertIsInstance(result, list)
        self.assertEqual(result, [])
        
    def test_shuffle_questions_order_list_less_than_10(self):
        result = shuffle_questions_order(self.questions)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(self.questions))

    def test_shuffle_questions_order_sample_is_shorter_than_population(self):
        result = shuffle_questions_order(self.questions, n_questions=3)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
    
    def test_shuffle_questions_order_sample_is_less_than_one(self):
        result = shuffle_questions_order(self.questions, n_questions=0)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

    def test_shuffle_questions_order_sample_is_longer_than_population(self):
        result = shuffle_questions_order(self.questions, n_questions=10)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 10)
    
    def test_shuffle_question_order_sample_is_longer_than_100(self):
        result = shuffle_questions_order(self.questions, n_questions=101)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 100)
        