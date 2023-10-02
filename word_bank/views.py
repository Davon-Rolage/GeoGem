from typing import Any
from django.db import models
from django.shortcuts import get_object_or_404, render
from django.http import request
from django.views.generic import ListView, DetailView
from word_bank.models import Block, WordInfo


class BlockListView(ListView):
    template_name = 'word_bank/learn.html'
    model = Block


class BlockDetailView(DetailView):
    template_name = 'word_bank/block_detail.html'
    model = Block

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        learning_block = self.get_object()
        block_words = WordInfo.objects.filter(blocks=learning_block)
        context['learning_block'] = learning_block
        context['block_words'] = block_words
        return context
    
    
