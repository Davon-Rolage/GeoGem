from django.shortcuts import render
from django.views.generic import View
from word_bank.models import Block, WordInfo
from secrets import choice
from django.http import HttpResponse


class QuizView(View):
    template_name = 'quizzer/quiz.html'
    model = Block
    
    def post(self, request):
        learning_block = request.POST.get('learning_block')
        block = Block.objects.get(slug=learning_block)
        words = WordInfo.objects.filter(blocks=block)[:5]
        for word in words:
            word.generate_options(block, n_wrong=3)
        
        context = {
            'learning_block': block,
            'words': words
        }

        return render(request, self.template_name, context=context)


def check_answer(request):
    if request.method == "POST":
        question_id = request.POST.get('question_id')
        word = WordInfo.objects.get(pk=question_id)
        answer = request.POST.get('answer')
        
        success = 'false'
        if answer == word.translation:
            success = 'true'
        
        return HttpResponse(success)

