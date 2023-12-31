from django.test import SimpleTestCase, tag
from django.urls import resolve, reverse

from word_bank.views import *


@tag("word_bank", "url", "url_word_bank")
class WordbankUrlsTestCase(SimpleTestCase):
    
    def test_learn_url_resolves(self):
        url = reverse('learn')
        self.assertEqual(resolve(url).func.view_class, BlockListView)
    
    def test_about_url_resolves(self):
        url = reverse('about')
        self.assertEqual(resolve(url).func.view_class, AboutView)

    def test_user_words_url_resolves(self):
        url = reverse('user_words')
        self.assertEqual(resolve(url).func.view_class, MyWordsListView)
    
    def test_user_block_words_url_resolves(self):
        url = reverse('user_block_words', args=['test-block'])
        self.assertEqual(resolve(url).func.view_class, UserBlockWordsListView)
    
    def test_add_word_info_url_resolves(self):
        url = reverse('add_word_info')
        self.assertEqual(resolve(url).func.view_class, AddWordInfoView)
    
    def test_edit_word_info_url_resolves(self):
        url = reverse('edit_word_info')
        self.assertEqual(resolve(url).func.view_class, EditWordInfoView)
    
    def test_blocks_table_url_resolves(self):
        url = reverse('blocks_table')
        self.assertEqual(resolve(url).func.view_class, EditBlocksView)
    
    def test_reset_test_block_url_resolves(self):
        url = reverse('reset_test_block')
        self.assertEqual(resolve(url).func.view_class, ResetTestBlockView)
    
    def test_block_detail_url_resolves(self):
        url = reverse('block_detail', args=['test-block'])
        self.assertEqual(resolve(url).func.view_class, BlockDetailView)
    
    def test_block_edit_url_resolves(self):
        url = reverse('block_edit', args=['test-block'])
        self.assertEqual(resolve(url).func.view_class, EditBlockDetailView)
