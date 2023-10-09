from collections import Counter

from django.views.generic import DetailView, ListView

from word_bank.models import Block, WordInfo, UserWord

from .config import MASTERY_LEVELS


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
    
        if self.request.user.is_authenticated:
            block_user_words = UserWord.objects.filter(user=self.request.user, word__blocks=learning_block)
            context['num_learned_words'] = block_user_words.count()
            
            block_mastery_level = learning_block.get_mastery_level(user=self.request.user)
            context['block_mastery_level'] = block_mastery_level
            context['block_mastery_level_pct'] = block_mastery_level / len(MASTERY_LEVELS) * 100

            word_mastery_levels = block_user_words.values_list('mastery_level', flat=True)
            context['ml_chart'] = get_ml_chart_data(word_mastery_levels)
            
        else:
            context['block_mastery_level'], context['block_mastery_level_pct'] = learning_block.get_mastery_level()
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
