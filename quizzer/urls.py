from django.urls import path
from .views import *


urlpatterns = [
    path('multi-choice/', QuizMultipleChoiceView.as_view(), name='quiz_multi_choice'),
    path('learn/', QuizLearnView.as_view(), name='quiz_learn'),
    path('add_to_learned/', add_to_learned, name='add_to_learned'),
    path('review/', QuizReviewView.as_view(), name='quiz_review'),
    path('check_answer_quiz/', check_answer_quiz, name='check_answer_quiz'),
    path('check_answer_review/', check_answer_review, name='check_answer_review'),
]
