import random

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from word_bank.models import Block, UserWord, WordInfo

from .models import Quiz


class QuizMultipleChoiceView(View):
    template_name = 'quizzer/quiz_multi_choice.html'
    model = Quiz
    
    def post(self, request):
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        block_words = WordInfo.objects.filter(blocks=block)
        for word in block_words:
            word.generate_options(block, n_wrong=3)

        words = shuffle(list(block_words))

        context = {
            'learning_block': block,
            'words': words
        }

        return render(request, self.template_name, context=context)


class QuizLearnView(View):
    template_name = 'quizzer/quiz_learn.html'
    model = Quiz
    
    def post(self, request):
        num_questions = 5
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        words = WordInfo.objects.filter(blocks=block)
        learned_words = UserWord.objects.filter(word__blocks=block, user=request.user)
        words_to_learn = []
        for word in words:
            if (len(words_to_learn) < num_questions) and (not learned_words.filter(word=word).exists()):
                words_to_learn.append(word)
        context = {
            'learning_block': block,
            'words': words_to_learn
        }

        return render(request, self.template_name, context=context)
    
    
class QuizReviewView(View):
    template_name = 'quizzer/quiz_review.html'
    model = Quiz
    
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
        
        words = shuffle(list(review_words))
        
        context = {
            'learning_block': block,
            'words': words
        }

        return render(request, self.template_name, context=context)


def check_answer_quiz(request):
    if request.method == "POST":
        success = None
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer')
        word = WordInfo.objects.get(pk=question_id)

        if request.user.is_authenticated:
            user_word, created = UserWord.objects.get_or_create(
                user=request.user,
                word=word
            )
            if answer == word.translation:
                success = 'true'
                user_word.points += 1
            else:
                success = 'false'
                user_word.points -= 1 if user_word.points > 0 else 0

            user_word.save()
        else:
            success = 'true' if answer == word.translation else 'false'
        
        return HttpResponse(success)


def check_answer_review(request):
    if request.method == "POST":
        success = None
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer')
        user_word = UserWord.objects.get(pk=question_id, user=request.user)
        word = WordInfo.objects.get(pk=user_word.word_id)
        
        if answer == word.translation:
            success = 'true'
            user_word.points += 1
        else:
            success = 'false'
            user_word.points -= 1 if user_word.points > 0 else 0

        user_word.save()
        
        return HttpResponse(success)

def add_to_learned(request):
    if request.method == "POST":
        success = 'true'
        question_id = request.POST.get('question_id')
        word = WordInfo.objects.get(pk=question_id)

        if request.user.is_authenticated:
            user_word, created = UserWord.objects.get_or_create(
                user=request.user,
                word=word
            )
            user_word.points += 1 if created else 0
            user_word.save()
        
        return HttpResponse(success)


def shuffle(words: list, n_questions=None):
    if n_questions is None:
        if len(words) <= 10:
            n_questions = 2 * len(words)
            words = 2 * words
        else:
            n_questions = len(words)
            
    shuffled_words = random.sample(words, n_questions)
    return shuffled_words
