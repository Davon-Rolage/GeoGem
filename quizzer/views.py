from django.shortcuts import render
from django.views.generic import View

from geogem.gui_messages import GUI_MESSAGES
from word_bank.models import Block, UserWord, WordInfo

from .utils import *


class QuizMultipleChoiceView(View):
    template_name = 'quizzer/quiz_multiple_choice.html'
    
    def post(self, request):
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        block_words = WordInfo.objects.filter(blocks=block)
        for word in block_words:
            word.generate_options(block, n_wrong=3)

        words = shuffle_options(list(block_words))
        if not words:
            return render(request, "quizzer/quiz_empty.html")

        context = {
            'gui_messages': GUI_MESSAGES['base'] | GUI_MESSAGES['quiz'],
            'learning_block': block,
            'words': words
        }

        return render(request, self.template_name, context=context)


class QuizLearnView(View):
    template_name = 'quizzer/quiz_learn.html'
    
    def post(self, request):
        num_questions = 5
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        words = WordInfo.objects.filter(blocks=block)
        user = request.user

        if user.is_authenticated:
            learned_words = UserWord.objects.filter(word__blocks=block, user=user)
            words_to_learn = []
            
            # Limit the number of quiz questions to num_questions
            for word in words:
                if (len(words_to_learn) < num_questions) and (not learned_words.filter(word=word).exists()):
                    words_to_learn.append(word)
                    
            context = {
                'learning_block': block,
                'words': words_to_learn,
            }

        else:
            context = {
                'learning_block': block,
                'words': words,
            }
        context['gui_messages'] = GUI_MESSAGES['base'] | GUI_MESSAGES['quiz']
        return render(request, self.template_name, context=context)
    
    
class QuizReviewView(View):
    template_name = 'quizzer/quiz_review.html'
    
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
        
        words = shuffle_options(list(review_words))
        if not words:
            return render(request, "quizzer/quiz_empty.html")
        
        distinct_words = set(words)
        context = {
            'gui_messages': GUI_MESSAGES['base'] | GUI_MESSAGES['quiz'],
            'learning_block': block,
            'words': words,
            'distinct_words': distinct_words,
        }

        return render(request, self.template_name, context=context)
    

class QuizResultsView(View):
    template_name = 'quizzer/quiz_results.html'
    
    def post(self, request):
        user = request.user
        learning_block_slug = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block_slug)
        block.is_completed = block.is_fully_learned(user)
        quiz_mode = request.POST.get('quiz_mode')

        quiz_words_ids = request.POST.get('quiz_words')
        if quiz_words_ids:
            quiz_words_ids = [int(word_id) for word_id in quiz_words_ids.split(',')]

        quiz_score = int(request.POST.get('quiz_score'))
        num_questions = request.POST.get('num_questions')        

        quiz_user_words = []
        for word_id in quiz_words_ids:
            if user.is_authenticated:
                word = UserWord.objects.get(pk=word_id, user=request.user)
            else:
                word = WordInfo.objects.get(pk=word_id)

            quiz_user_words.append(word)
            
        context = {
            'gui_messages': GUI_MESSAGES['base'] | GUI_MESSAGES['quiz_results'] | GUI_MESSAGES['block_detail'] | GUI_MESSAGES['column_titles'] | GUI_MESSAGES['tooltips'],
            'learning_block': block,
            'quiz_mode': quiz_mode,
            'quiz_words': quiz_user_words,
            'quiz_score': quiz_score,
            'num_questions': num_questions,
        }
        return render(request, self.template_name, context=context)
