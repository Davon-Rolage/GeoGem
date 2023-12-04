import random

from django.http import JsonResponse

from word_bank.models import UserWord, WordInfo


def update_user_word_points(user_answer, correct_answer, user_word) -> bool:
    """
    Updates the word points for a user based on their answer.

    Args:
        user_answer (any): The user's answer.
        correct_answer (any): The correct answer.
        user_word (UserWord): The user's word object.

    Returns:
        bool: True if the user's answer is correct, False otherwise.
    """
    if user_answer == correct_answer:
        is_correct = True
        user_word.points = min(100, user_word.points + 1)

    else:
        is_correct = False
        user_word.points = max(0, user_word.points - 1)
        
    user_word.save()
    return is_correct


def add_to_learned(request):
    if request.method == "POST":
        question_id = request.POST.get('question_id')
        is_last = request.POST.get('is_last') == 'true'
        word = WordInfo.objects.get(pk=question_id)
        user = request.user
        json_data = dict()

        if user.is_authenticated:
            user_word, created = UserWord.objects.get_or_create(
                user=user,
                word=word
            )
            user_word.points += int(created)
            user_word.save()
            json_data = {
                'created': created,
                'user_word_id': user_word.id,
            }
        json_data.update({'is_last': is_last})
        return JsonResponse(json_data)


def check_answer_multiple_choice(request):
    if request.method == "POST":
        question_id = request.POST.get('question_id')
        word = WordInfo.objects.get(pk=question_id)
        
        user_answer = request.POST.get('answer')
        correct_answer = word.translation

        if request.user.is_authenticated:
            user_word, created = UserWord.objects.get_or_create(
                user=request.user,
                word=word
            )
            is_correct = update_user_word_points(user_answer, correct_answer, user_word)
        else:
            is_correct = user_answer == correct_answer
        
        example_span = populate_example_span(word) if is_correct else ''

        return JsonResponse({
            'is_correct': is_correct,
            'example_span': example_span
        })


def check_answer_review(request):
    if request.method == "POST":
        question_id = request.POST.get('question_id')
        user_word = UserWord.objects.get(pk=question_id, user=request.user)
        word = WordInfo.objects.get(pk=user_word.word_id)

        user_answer = request.POST.get('answer')
        correct_answer = word.translation

        is_correct = update_user_word_points(user_answer, correct_answer, user_word)
        example_span = populate_example_span(word) if is_correct else ''
                
        return JsonResponse({
            'is_correct': is_correct,
            'example_span': example_span
        })


def populate_example_span(word):
    example_span = ''
    word_example = word.example if word.example else None
    word_example_image = word.example_image.url if word.example_image else None
    
    if word_example_image:
        example_span += f'<img src="{ word.example_image.url }" class="image-example" alt="example_image"> '
    
    if word_example:
        example_span += word.example
        
    return example_span


def shuffle_options(words: list, n_questions=None):
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
