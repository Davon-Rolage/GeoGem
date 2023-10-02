from django.urls import path
from .views import QuizView, check_answer


urlpatterns = [
    # path('run_quiz/<slug:slug>', QuizView.as_view(), name='run_quiz'),
    path('run_quiz/', QuizView.as_view(), name='run_quiz'),
    path('check_answer/', check_answer, name='check_answer'),
]
