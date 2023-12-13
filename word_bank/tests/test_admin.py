from django.test import RequestFactory, TestCase, tag

from word_bank.admin import (AdvancedUserWordMasteryLevelListFilter,
                             BlockAdmin, BlockIsBasicListFilter, UserWordAdmin)
from word_bank.models import Block, UserWord
from django.contrib.auth import get_user_model


@tag("word_bank", "admin", "admin_block_list_filter")
class BlockIsBasicListFilterTest(TestCase):

    def test_lookups(self):
        self.assertEqual(BlockIsBasicListFilter.lookups(None, None, None), [
            ('true', 'Basic'),
            ('false', 'Not Basic'),
        ])
    
    def test_queryset(self):
        basic_block = Block.objects.create(name='Basic Words')
        basic_block2 = Block.objects.create(name='Basics')
        advanced_block = Block.objects.create(name='Advanced Words')
        
        filter_basic = BlockIsBasicListFilter(
            request=None, params={'is_basic': 'true'}, 
            model=None, model_admin=None
        )
        filter_not_basic = BlockIsBasicListFilter(
            request=None, params={'is_basic': 'false'}, 
            model=None, model_admin=None
        )

        # Test the queryset when the filter is set to 'basic'
        queryset_basic = filter_basic.queryset(request=None, queryset=Block.objects.all())
        self.assertEqual(len(queryset_basic), 2)
        self.assertEqual(list(queryset_basic.values_list('name', flat=True)), ['Basic Words', 'Basics'])
        
        # Test the queryset when the filter is set to 'not_basic'
        queryset_not_basic = filter_not_basic.queryset(request=None, queryset=Block.objects.all())
        self.assertEqual(len(queryset_not_basic), 1)
        self.assertEqual(list(queryset_not_basic.values_list('name', flat=True)), ['Advanced Words'])


@tag("word_bank", "admin", "admin_word_mastery_list_filter")
class AdvancedUserWordMasteryLevelListFilterTest(TestCase):
    ...
            
        
    