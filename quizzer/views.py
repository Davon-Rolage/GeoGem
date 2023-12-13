from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from geogem.gui_messages import get_gui_messages
from word_bank.models import Block, UserWord, WordInfo

from .utils import *


class QuizMultipleChoiceView(View):
    template_name = 'quizzer/quiz_multiple_choice.html'
    gui_messages = get_gui_messages(['base', 'quiz'])
    
    def post(self, request):
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        block_words = WordInfo.objects.filter(blocks=block)
        for word in block_words:
            word.generate_options(block, n_wrong=3)

        words = shuffle_questions_order(list(block_words))
        if not words:
            return render(request, "quizzer/quiz_empty.html")

        context = {
            'gui_messages': self.gui_messages,
            'learning_block': block,
            'words': words
        }

        return render(request, self.template_name, context=context)


class QuizLearnView(View):
    template_name = 'quizzer/quiz_learn.html'
    gui_messages = get_gui_messages(['base', 'quiz'])
    
    def post(self, request):
        num_questions = 5
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        words = WordInfo.objects.filter(blocks=block)
        user = request.user

        if user.is_authenticated:
            learned_words = UserWord.objects.filter(word__blocks=block, user=user)
            words_to_learn = words.exclude(id__in=learned_words.values_list('word', flat=True))
            words_to_learn = shuffle_questions_order(list(words_to_learn), num_questions)
            
            context = {
                'learning_block': block,
                'words': words_to_learn,
            }

        else:
            context = {
                'learning_block': block,
                'words': words,
            }
        context['gui_messages'] = self.gui_messages
        return render(request, self.template_name, context=context)
    
    
class QuizReviewView(LoginRequiredMixin, View):
    template_name = 'quizzer/quiz_review.html'
    gui_messages = get_gui_messages(['base', 'quiz'])
    
    def post(self, request):
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        user_words = UserWord.objects.filter(word__blocks=block, user=request.user)

        review_words = []
        for word in user_words:
            # Generate wrong options for each word in user_words
            info_word = WordInfo.objects.get(pk=word.word.id)
            info_word.generate_options(block, n_wrong=3)
            word.options = info_word.options
            review_words.append(word)
        
        words = shuffle_questions_order(list(review_words))
        if not words:
            return render(request, "quizzer/quiz_empty.html")
        
        distinct_words = set(words)
        context = {
            'gui_messages': self.gui_messages,
            'learning_block': block,
            'words': words,
            'distinct_words': distinct_words,
        }

        return render(request, self.template_name, context=context)
    

class QuizResultsView(View):
    template_name = 'quizzer/quiz_results.html'
    gui_messages = get_gui_messages(
        ['base', 'quiz_results', 'block_detail', 'column_titles', 'tooltips']
    )
    
    def post(self, request):
        user = request.user
        learning_block_slug = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block_slug)
        block.is_completed = block.is_fully_learned(user)
        quiz_type = request.POST.get('quiz_type')

        quiz_words_ids = request.POST.get('quiz_words') or ''
        if not quiz_words_ids:
            context = {
                'gui_messages': self.gui_messages,
                'learning_block': block,
                'quiz_type': quiz_type,
                'quiz_words': [],
            }
            return render(request, self.template_name, context=context)

        quiz_words_ids = [int(word_id) for word_id in quiz_words_ids.split(',')]
        quiz_score = int(request.POST.get('quiz_score'))
        num_questions = request.POST.get('num_questions')        

        quiz_user_words = []
        for word_id in quiz_words_ids:
            if user.is_authenticated:
                word = UserWord.objects.get(pk=word_id, user=user)
            else:
                word = WordInfo.objects.get(pk=word_id)

            quiz_user_words.append(word)
            
        context = {
            'gui_messages': self.gui_messages,
            'learning_block': block,
            'quiz_type': quiz_type,
            'quiz_words': quiz_user_words,
            'quiz_score': quiz_score,
            'num_questions': num_questions,
        }
        return render(request, self.template_name, context=context)


class CheckAnswerView(View):
    quiz_type_functions = {
        'multiple_choice': check_answer_multiple_choice,
        'review': check_answer_review,
    }
    
    def post(self, request):
        quiz_type = request.POST.get('quiz_type')
        
        try:
            return self.quiz_type_functions[quiz_type](request)
        
        except KeyError:
            return HttpResponse(status=400)
    