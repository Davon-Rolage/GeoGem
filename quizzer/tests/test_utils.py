from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from quizzer.utils import *
from word_bank.models import Block, UserWord, WordInfo


class UpdateUserWordPointsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = get_user_model().objects.create_user(username='test_user', password='test_password', is_active=True)
        cls.test_word_info = WordInfo.objects.create(name='test_name', translation='test')
        cls.test_user_word = UserWord.objects.create(user=cls.test_user, word=cls.test_word_info, points=50)

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
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.user_profile = cls.user.profile
        cls.user_profile.experience = 50
        cls.user_profile.save()

    def test_update_profile_experience_default_increase(self):
        update_profile_experience(self.user)
        self.user_profile.refresh_from_db(fields=['experience'])
        
        self.assertEqual(self.user_profile.experience, 51)

    def test_update_profile_experience_increase_by_10(self):
        update_profile_experience(self.user, increase_by=10)
        self.user_profile.refresh_from_db(fields=['experience'])

        self.assertEqual(self.user_profile.experience, 60)


class AddToLearnedTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()
        cls.url = reverse('add_to_learned')
        
        cls.test_word_info = WordInfo.objects.create(name='test_name', translation='test')
        cls.request_data = {'question_id': cls.test_word_info.id, 'is_last': 'true'}

        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_with_words = cls.User.objects.create_user(
            username='test_user_with_words', password='test_password', is_active=True
        )

    def test_add_to_learned_as_anonymous_user_POST(self):
        response = self.client.post(self.url, self.request_data)
        response_content = response.content.decode('utf-8')
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response_content, {'is_last': True})
        
    def test_add_to_learned_as_authenticated_user_created_word_POST(self):
        self.client.force_login(self.test_user)
        response = self.client.post(self.url, self.request_data)
        response_content = response.content.decode('utf-8')
        
        user_word = UserWord.objects.get(user=self.test_user, word=self.test_word_info)
        
        test_user_profile = self.test_user.profile
        test_user_profile.refresh_from_db(fields=['num_learned_words'])
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_user_profile.num_learned_words, 1)
        self.assertEqual(user_word.points, 1)
        self.assertJSONEqual(response_content, {
            'is_last': True,
            'created': True,
            'user_word_id': user_word.id
        })
    
    def test_add_to_learned_as_authenticated_user_known_word_POST(self):
        UserWord.objects.create(user=self.test_user_with_words, word=self.test_word_info, points=20)

        self.client.force_login(self.test_user_with_words)
        response = self.client.post(self.url, self.request_data)
        response_content = response.content.decode('utf-8')

        user_word = UserWord.objects.get(user=self.test_user_with_words, word=self.test_word_info)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_word.points, 20)
        self.assertJSONEqual(response_content, {
            'is_last': True,
            'created': False,
            'user_word_id': user_word.id
        })


class CheckAnswerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.client = Client()

        cls.url = reverse('check_answer')
        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_word_info = WordInfo.objects.create(name='test_name', translation='test')
        cls.test_word_info.blocks.add(cls.test_block)

        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        cls.test_user_profile = cls.test_user.profile
        cls.test_user_profile.experience = 50
        cls.test_user_profile.save()
        cls.test_user_word = UserWord.objects.create(
            user=cls.test_user, word=cls.test_word_info, points=1
        )
    
    def test_check_answer_view_method_not_allowed_GET(self):
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
        self.client.force_login(self.test_user)
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user_profile.experience - profile_exp_before, 2)
        self.assertEqual(self.test_user_word.points - user_word_points_before, 2)
        self.assertJSONEqual(response_content, {
            'is_correct': True,
            'example_span': ''
        })

    def test_check_answer_multiple_choice_incorrect_answer_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user)
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user_profile.experience, profile_exp_before)
        self.assertEqual(self.test_user_word.points - user_word_points_before, -1)
        self.assertJSONEqual(response_content, {
            'is_correct': False,
            'example_span': ''
        })

    
    def test_check_answer_review_correct_answer_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user)
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user_profile.experience - profile_exp_before, 1)
        self.assertEqual(self.test_user_word.points - user_word_points_before, 1)
        
        self.assertJSONEqual(response_content, {
            'is_correct': True,
            'example_span': ''
        })
    
    def test_check_answer_review_incorrect_answer_as_authenticated_user_POST(self):
        self.client.force_login(self.test_user)
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user_profile.experience, profile_exp_before)
        self.assertEqual(self.test_user_word.points - user_word_points_before, -1)
        
        self.assertJSONEqual(response_content, {
            'is_correct': False,
            'example_span': ''
        })


class PopulateExampleSpanTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_example_text = "example_text"
        cls.test_example_image_url = "example_image_url"
        
        cls.word_empty = WordInfo()
        cls.word_example_text = WordInfo(example=cls.test_example_text)
        cls.word_example_image = WordInfo(example_image=cls.test_example_image_url)
        cls.word_example_text_and_image = WordInfo(
            example=cls.test_example_text, example_image=cls.test_example_image_url
        )

    def test_populate_example_span_without_example(self):
        result = populate_example_span(self.word_empty)
        self.assertEqual(result, "")
        
    def test_populate_example_span_with_example_text(self):
        result = populate_example_span(self.word_example_text)
        self.assertEqual(result, self.test_example_text)

    def test_populate_example_span_with_example_image(self):
        result = populate_example_span(self.word_example_image)
        
        self.assertIn("<img", result)
        self.assertIn(self.test_example_image_url, result)

    def test_populate_example_span_with_both_example_text_and_image(self):
        result = populate_example_span(self.word_example_text_and_image)
        
        self.assertIn("<img", result)
        self.assertIn(self.test_example_image_url, result)
        self.assertIn(self.test_example_text, result)


class ShuffleQuestionsOrderTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.questions = [x for x in range(1, 5)]

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
        