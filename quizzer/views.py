from django.shortcuts import render
from django.views.generic import View
from word_bank.models import Block, WordInfo, UserWord
from secrets import choice
from django.http import HttpResponse


class QuizView(View):
    template_name = 'quizzer/quiz.html'
    model = Block
    
    def post(self, request):
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        words = WordInfo.objects.filter(blocks=block)
        for word in words:
            word.generate_options(block, n_wrong=3)
        
        context = {
            'learning_block': block,
            'words': words
        }

        return render(request, self.template_name, context=context)


def check_answer(request):
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

