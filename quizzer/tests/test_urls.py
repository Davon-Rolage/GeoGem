from django.test import SimpleTestCase, tag
from django.urls import resolve, reverse

from quizzer.views import *


@tag("quizzer", "url", "url_quizzer")
class QuizzerUrlsTestCase(SimpleTestCase):
    
    def test_quiz_learn_url_resolves(self):
        url = reverse('quiz_learn')
        self.assertEqual(resolve(url).func.view_class, QuizLearnView)
    
    def test_quiz_multiple_choice_url_resolves(self):
        url = reverse('quiz_multiple_choice')
        self.assertEqual(resolve(url).func.view_class, QuizMultipleChoiceView)
    
    def test_quiz_review_url_resolves(self):
        url = reverse('quiz_review')
        self.assertEqual(resolve(url).func.view_class, QuizReviewView)
    
    def test_quiz_results_url_resolves(self):
        url = reverse('quiz_results')
        self.assertEqual(resolve(url).func.view_class, QuizResultsView)

    def test_check_answer_view_url_resolves(self):
        url = reverse('check_answer')
        self.assertEqual(resolve(url).func.view_class, CheckAnswerView)

    def test_add_to_learned_url_resolves(self):
        url = reverse('add_to_learned')
        self.assertEqual(resolve(url).func, add_to_learned)
    