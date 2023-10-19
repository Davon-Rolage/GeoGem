import json
import random

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View

from word_bank.models import Block, UserWord, WordInfo


class QuizMultipleChoiceView(View):
    template_name = 'quizzer/quiz_multi_choice.html'
    
    def post(self, request):
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        block_words = WordInfo.objects.filter(blocks=block)
        for word in block_words:
            word.generate_options(block, n_wrong=3)

        words = shuffle(list(block_words))
        if not words:
            return render(request, "quizzer/quiz_empty.html")

        context = {
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

        if request.user.is_authenticated:
            learned_words = UserWord.objects.filter(word__blocks=block, user=request.user)
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
        
        words = shuffle(list(review_words))
        if not words:
            return render(request, "quizzer/quiz_empty.html")
        
        distinct_words = set(words)            
        context = {
            'learning_block': block,
            'words': words,
            'distinct_words': distinct_words,
        }

        return render(request, self.template_name, context=context)


def update_user_word_points(user_answer, correct_answer, user_word) -> str:
    """
    Update the points of a user word based on the user's answer and the correct answer.

    Parameters:
    - user_answer (str): The user's answer to the word.
    - correct_answer (str): The correct answer to the word.
    - user_word (UserWord): The user word object.

    Returns:
    - str: The success status of the update ('true' or 'false').

    Remarks:
    - If the user's answer matches the correct answer, the user's word points will be incremented by 1, capped at 100.
    - If the user's answer does not match the correct answer, the user's word points will be decremented by 1, capped at 0.
    - The updated user word object will be saved to the database.
    """
    if user_answer == correct_answer:
        success = 'true'
        user_word.points = min(100, user_word.points + 1)

    else:
        success = 'false'
        user_word.points = max(0, user_word.points - 1)
        
    user_word.save()
    return success


def check_answer_quiz(request):
    if request.method == "POST":
        question_id = request.POST.get('question_id')
        word = WordInfo.objects.get(pk=question_id)
        
        user_answer = request.POST.get('answer')
        correct_answer = word.translation
        example_span = ''

        if request.user.is_authenticated:
            user_word, created = UserWord.objects.get_or_create(
                user=request.user,
                word=word
            )
            success = update_user_word_points(user_answer, correct_answer, user_word)
        else:
            success = 'true' if user_answer == correct_answer else 'false'
        
        json_data = json.dumps([
            {
                'success': success,
                'example_span': example_span,
            }
        ]) 
        
        return HttpResponse(json_data)


def check_answer_review(request):
    if request.method == "POST":
        question_id = request.POST.get('question_id')
        user_word = UserWord.objects.get(pk=question_id, user=request.user)
        word = WordInfo.objects.get(pk=user_word.word_id)

        user_answer = request.POST.get('answer')
        correct_answer = word.translation

        success = update_user_word_points(user_answer, correct_answer, user_word)
        example_span = populate_example_span(success, word)
                
        json_data = json.dumps([
            {
                'success': success,
                'example_span': example_span,
            }
        ])   
        return HttpResponse(json_data)


def populate_example_span(success, word):
    example_span = ''
    if success == 'true':
        word_example = word.example if word.example else None
        word_example_image = word.example_image.url if word.example_image else None
        
        if word_example_image:
            example_span += f'<img src="{ word.example_image.url }" alt="example_image" style="max-height: 30px;"> '
        
        if word_example:
            example_span += word.example
        
    return example_span


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
    if len(words) == 0:
        return 0
    
    if len(words) <= 5:
        n_questions = 5
    
    if n_questions is None:
        n_questions = 10
            
    if n_questions > len(words):
        words *= (n_questions // len(words) + 1)
        
    shuffled_words = random.sample(words, n_questions)
    return shuffled_words
