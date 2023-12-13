from random import sample

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from word_bank.models import UserWord, WordInfo


def update_user_word_points(user_answer: str, correct_answer: str, user_word: UserWord, increase_by=1, decrease_by=1) -> bool:
    if user_answer == correct_answer:
        is_correct = True
        user_word.points = min(100, user_word.points + increase_by)

    else:
        is_correct = False
        user_word.points = max(0, user_word.points - decrease_by)
        
    user_word.save()
    return is_correct


def update_profile_experience(user, increase_by=1):
    user_profile = user.profile
    user_profile.experience += increase_by
    user_profile.save()


@require_POST
def add_to_learned(request):
    question_id = request.POST.get('question_id')
    is_last = request.POST.get('is_last') == 'true'
    word = WordInfo.objects.get(pk=question_id)
    user = request.user
    json_data = dict()
    
    if user.is_authenticated:
        user_profile = user.profile
        user_word, created = UserWord.objects.get_or_create(
            user=user,
            word=word
        )
        user_word.points += int(created)
        if created:
            user_profile.num_learned_words += 1
            user_profile.save()
            update_profile_experience(user, increase_by=1)

        user_word.save()
        json_data = {
            'created': created,
            'user_word_id': user_word.id,
        }
    json_data.update({'is_last': is_last})
    return JsonResponse(json_data)


def check_answer_multiple_choice(request):
    question_id = request.POST.get('question_id')
    word = WordInfo.objects.get(pk=question_id)
    
    user_answer = request.POST.get('answer')
    correct_answer = word.translation
    user = request.user
    if user.is_authenticated:
        user_word, created = UserWord.objects.get_or_create(
            user=user,
            word=word
        )
        is_correct = update_user_word_points(user_answer, correct_answer, user_word, increase_by=2, decrease_by=1)
        if is_correct:
            update_profile_experience(user, increase_by=2)
    else:
        is_correct = user_answer == correct_answer
    
    example_span = populate_example_span(word) if is_correct else ''

    return JsonResponse({
        'is_correct': is_correct,
        'example_span': example_span
    })


def check_answer_review(request):
    question_id = request.POST.get('question_id')
    user = request.user
    user_word = UserWord.objects.get(pk=question_id, user=user)
    word = WordInfo.objects.get(pk=user_word.word_id)

    user_answer = request.POST.get('answer')
    correct_answer = word.translation

    is_correct = update_user_word_points(user_answer, correct_answer, user_word, increase_by=1, decrease_by=1)
    if is_correct:
        example_span = populate_example_span(word)
        update_profile_experience(user, increase_by=1)

    else:
        example_span = ''
            
    return JsonResponse({
        'is_correct': is_correct,
        'example_span': example_span
    })


def populate_example_span(word):
    example_span = ''
    word_example = word.example if word.example else None
    word_example_image = word.example_image.url if word.example_image else None
    
    if word_example_image:
        example_span += f'<img src="{ word_example_image }" class="image-example" alt="example_image"> '
    
    if word_example:
        example_span += word.example
        
    return example_span


def shuffle_questions_order(words: list, n_questions=None):
    if not words or not isinstance(words, list):
        return []
    
    if n_questions is None:
        n_questions = min(10, len(words))
    else:
        n_questions = min(100, max(1, n_questions))
        if n_questions > len(words):
            repetition_factor = (n_questions // len(words) + 1)
            words *= repetition_factor
        
    shuffled_words = sample(words, n_questions)
    return shuffled_words
