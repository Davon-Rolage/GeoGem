from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, View
from django.views.generic.base import TemplateView

from geogem.gui_messages import get_gui_messages

from .models import Block, UserWord, WordInfo
from .utils import *


class BlockListView(ListView):
    template_name = 'word_bank/learn.html'
    model = Block
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        blocks = context['object_list']
        for block in blocks:
            block.is_completed = block.is_fully_learned(user)
        
        context['gui_messages'] = get_gui_messages(['base', 'learn_index', 'block_detail'])
        context['learning_blocks'] = blocks
        context['user_profile'] = user.profile if user.is_authenticated else None
        return context


class BlockDetailView(DetailView):
    template_name = 'word_bank/block_detail.html'
    model = Block

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gui_messages = get_gui_messages(['base', 'tooltips', 'block_detail'])
        user = self.request.user
        learning_block = self.get_object()
        learning_block.is_completed = learning_block.is_fully_learned(user)
        block_words = WordInfo.objects.filter(blocks=learning_block)
        
        block_mastery_level = learning_block.get_mastery_level(user=user)
        bml_whole_part, bml_fractional_part = divmod(block_mastery_level, 1)
    
        if user.is_authenticated:
            num_learned_words = UserWord.objects.filter(user=user, word__blocks=learning_block).count()
            block_user_words = UserWord.objects.filter(user=user, word__blocks=learning_block)
            word_mastery_levels = [word.mastery_level for word in block_user_words]
            context.update({
                'gui_messages': gui_messages,
                'learning_block': learning_block,
                'block_words': block_words,
                'num_learned_words': num_learned_words,
                'block_mastery_level': block_mastery_level,
                'bml_whole_part': bml_whole_part,
                'bml_fractional_part': round(bml_fractional_part, 3),
                'ml_chart': get_ml_chart_data(word_mastery_levels),
            })
        else:
            context.update({
                'gui_messages': gui_messages,
                'learning_block': learning_block,
                'block_words': block_words,
                'block_mastery_level': block_mastery_level,
                'ml_chart': get_ml_chart_data(),
            })
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class EditBlocksView(View):
    template_name = 'word_bank/blocks_table.html'
    model = Block
    
    def get(self, request):
        blocks = Block.objects.all().order_by('-updated_at')
        for block in blocks:
            block.word_count = WordInfo.objects.filter(blocks=block).count()
        
        context = {
            'gui_messages': get_gui_messages(['base']),
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
        block_words = WordInfo.objects.filter(blocks=learning_block).order_by('-updated_at')
        
        context['gui_messages'] = get_gui_messages(['base', 'column_titles'])
        context['learning_block'] = learning_block
        context['block_words'] = block_words
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class AddWordInfoView(View):
    model = WordInfo
    
    def post(self, request):
        learning_block_id = request.POST.get('learning_block_id')
        word = self.model.objects.create(
            name='new_name',
            transliteration='new_transliteration',
            translation='new_translation'
        )
        word.blocks.add(learning_block_id)
        word.save()
        return JsonResponse({
            'success': True
        })


@method_decorator(staff_member_required, name='dispatch')
class EditWordInfoView(View):
    model = WordInfo
    
    def post(self, request, *args, **kwargs):
        word_id = request.POST.get('word_id')
        word = self.model.objects.get(pk=word_id)
        changed_field = request.POST.get('changed_field')
        new_value = request.POST.get('new_value')
        old_value = getattr(word, changed_field)
        updated_at = word.updated_at.strftime('%H:%M:%S %d-%m-%Y')
        setattr(word, changed_field, new_value)
        word.save()
        return JsonResponse({
            'success': True,
            'word_id': word_id,
            'changed_field': changed_field,
            'old_value': old_value,
            'new_value': new_value,
            'updated_at': updated_at
        })
    
    
class MyWordsListView(LoginRequiredMixin, ListView):
    template_name = 'word_bank/user_words.html'
    model = UserWord
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        words = self.model.objects.filter(user=user).order_by('-added_at')
        context['words'] = words
        context['gui_messages'] = get_gui_messages(['base', 'column_titles', 'my_words_title'])
        return context


class UserBlockWordsListView(ListView):
    template_name = 'word_bank/user_block_words.html'
    context_object_name = 'user_words'
    model = UserWord
    
    def get_queryset(self):
        user = self.request.user
        slug = self.kwargs['slug']
        learning_block = Block.objects.get(slug=slug)
        if user.is_authenticated:
            return self.model.objects.filter(user=user, word__blocks=learning_block).order_by('-added_at')

        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        context['learning_block'] = Block.objects.get(slug=slug)
        context['gui_messages'] = get_gui_messages(['base', 'column_titles'])
        return context
    

class AboutView(TemplateView):
    template_name = 'word_bank/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gui_messages'] = get_gui_messages(['base', 'about'])
        return context
    

@method_decorator(staff_member_required, name='dispatch')
class ResetTestBlockView(View):
    def post(self, request):
        user = request.user
        test_words = UserWord.objects.filter(user=user, word__blocks__id=0)
        test_words.delete()
        return JsonResponse({'success': True})
    