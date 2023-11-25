from django.urls import path
from .views import *


urlpatterns = [
    path('learn/', QuizLearnView.as_view(), name='quiz_learn'),
    path('multiple_choice/', QuizMultipleChoiceView.as_view(), name='quiz_multiple_choice'),
    path('review/', QuizReviewView.as_view(), name='quiz_review'),
    
    path('add_to_learned/', add_to_learned, name='add_to_learned'),
    path('check_answer_multiple_choice/', check_answer_multiple_choice, name='check_answer_multiple_choice'),
    path('check_answer_review/', check_answer_review, name='check_answer_review'),
    
    path('results/', QuizResultsView.as_view(), name='quiz_results'),
]
