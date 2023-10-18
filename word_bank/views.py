from collections import Counter

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View, DetailView, ListView

from word_bank.models import Block, WordInfo, UserWord

from .config import MASTERY_LEVELS


class BlockListView(ListView):
    template_name = 'word_bank/learn.html'
    model = Block
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        blocks = context['object_list']
        block_fully_learned_list = [block.is_fully_learned(user) for block in blocks]
        context['block_list'] = zip(blocks, block_fully_learned_list)
        return context


class BlockDetailView(DetailView):
    template_name = 'word_bank/block_detail.html'
    model = Block

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_block = self.get_object()
        block_words = WordInfo.objects.filter(blocks=learning_block)
        
        context['learning_block'] = learning_block
        context['block_words'] = block_words
    
        if self.request.user.is_authenticated:
            block_user_words = UserWord.objects.filter(user=self.request.user, word__blocks=learning_block)
            context['num_learned_words'] = block_user_words.count()
            
            block_mastery_level = learning_block.get_mastery_level(user=self.request.user)

            bml_whole_part, bml_fractional_part = divmod(block_mastery_level, 1)
            context['bml_whole_part'] = bml_whole_part
            context['bml_fractional_part'] = round(bml_fractional_part, 3)

            context['block_mastery_level_pct'] = block_mastery_level / len(MASTERY_LEVELS) * 100

            word_mastery_levels = block_user_words.values_list('mastery_level', flat=True)
            context['ml_chart'] = get_ml_chart_data(word_mastery_levels)
            
        else:
            block_mastery_level = learning_block.get_mastery_level(user=self.request.user)
            context['block_mastery_level_pct'] = block_mastery_level / len(MASTERY_LEVELS) * 100
            context['ml_chart'] = get_ml_chart_data()
        
        return context


def get_ml_chart_data(mastery_levels=None):
    mastery_levels_dct = dict(Counter(mastery_levels))
    for level in MASTERY_LEVELS.keys():
        if level not in mastery_levels_dct:
            mastery_levels_dct[level] = 0

    mastery_levels_dct = dict(sorted(mastery_levels_dct.items()))
    x = sorted(list(mastery_levels_dct.keys()))
    y = list(mastery_levels_dct.values())
    return {'x': x, 'y': y}


def staff_member_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=reverse_lazy('login')
    )
    return decorated_view_func(view_func)


@method_decorator(staff_member_required, name='dispatch')
class EditBlocksView(View):
    template_name = 'word_bank/blocks_table.html'
    model = Block
    
    def get(self, request):
        blocks = Block.objects.all().order_by('-updated_at')
        for block in blocks:
            block.word_count = WordInfo.objects.filter(blocks=block).count()
        
        context = {
            'blocks': blocks
        }            
        return render(request, self.template_name, context=context)


@method_decorator(staff_member_required, name='dispatch')
class EditBlockDetailView(DetailView):
    template_name = 'word_bank/block_edit.html'
    model = Block
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_block = self.get_object()
        block_words = WordInfo.objects.filter(blocks=learning_block)
        
        context['learning_block'] = learning_block
        context['block_words'] = block_words
        
        return context
    
    
class MyWordsListView(ListView):
    template_name = 'word_bank/user_words.html'
    model = UserWord
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_words = self.model.objects.filter(user=user).order_by('-added_at') if user.is_authenticated else []
        context['words'] = user_words
        return context


class UserBlockDetailView(DetailView):
    template_name = 'word_bank/user_block_detail.html'
    model = Block
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_words = UserWord.objects.filter(user=user, word__blocks=self.get_object()) if user.is_authenticated else []
        context = {
            'learning_block': self.get_object(),
            'words': user_words,
        }
        return context
    
