from django.test import TestCase

from accounts.models import CustomUser
from word_bank.models import Block, UserWord, WordInfo
from django.contrib.auth.models import AnonymousUser


class TestModels(TestCase):
    
    def setUp(self):
        self.test_block = Block.objects.create(name='Test Block')
        self.test_block_with_custom_slug = Block.objects.create(name='Test Slug', slug='test_custom_slug')
        self.test_block_with_empty_name = Block.objects.create(name=' ')

        self.test_word_info = WordInfo.objects.create(name='Test Word', translation='Test Word Translation')
        self.test_word_info.blocks.add(self.test_block)
        self.test_word_info2 = WordInfo.objects.create(name='Test Word 2', translation='Test Word 2 Translation')
        self.test_word_info2.blocks.add(self.test_block)
        self.test_word_info_full = WordInfo.objects.create(
            name='Test Word Full Name', transliteration='Test Word Full Transliteration', 
            translation='Test Word Full Translation', example='Test Word Long Example'
        )
        self.test_word_info_full.blocks.add(self.test_block)
        self.test_word_info_short_example = WordInfo.objects.create(
            name='Test Word Short Name', transliteration='Test Word Transliteration', 
            translation='Test Word Short Example Translation', example='Short Example'
        )
        self.test_word_info_short_example.blocks.add(self.test_block)
        self.test_word_info_no_example = WordInfo.objects.create(name='Test Word Name No Example', translation='Test Word No Example Translation')
        self.test_word_info_no_example.blocks.add(self.test_block)

        self.test_user_has_words = CustomUser.objects.create(username='test_user_has_words', is_active=True)
        UserWord.objects.create(user=self.test_user_has_words, word=self.test_word_info, points=1)
        self.test_user_word = UserWord.objects.get(user=self.test_user_has_words, word=self.test_word_info)
        UserWord.objects.create(user=self.test_user_has_words, word=self.test_word_info2)
        self.test_user_word2 = UserWord.objects.get(user=self.test_user_has_words, word=self.test_word_info2)

        self.test_user_no_words = CustomUser.objects.create(username='test_user_no_words', is_active=True)
        self.test_user_anonymous = AnonymousUser()
        
        self.test_user_all_words_learned = CustomUser.objects.create(username='test_user_all_words_learned', is_active=True)
        for word_info in WordInfo.objects.all():
            UserWord.objects.create(user=self.test_user_all_words_learned, word=word_info)
        for user_word in UserWord.objects.filter(user=self.test_user_all_words_learned):
            user_word.points = 1
            user_word.save()
        
    def test_block_str(self):
        self.assertEquals(str(self.test_block), 'Test Block')

    def test_block_default_slug_is_assigned_on_save(self):
        self.test_block.save()
        self.assertEquals(self.test_block.slug, 'test-block')
        
    def test_block_custom_slug_is_preserved_on_save(self):
        self.test_block_with_custom_slug.save()
        self.assertEquals(self.test_block_with_custom_slug.slug, 'test_custom_slug')

    def test_block_default_slug_is_assigned_on_save(self):
        self.test_block_with_empty_name.save()
        self.assertEquals(self.test_block_with_empty_name.slug, 'new-block')
    
    def test_block_get_mastery_level_user_has_words(self):
        test_user_block_mastery_level = self.test_block.get_mastery_level(self.test_user_has_words)
        self.assertEquals(test_user_block_mastery_level, 0.2)
    
    def test_block_get_mastery_level_user_no_words(self):
        test_user_block_mastery_level = self.test_block.get_mastery_level(self.test_user_no_words)
        self.assertEquals(test_user_block_mastery_level, 0)
    
    def test_block_get_mastery_level_user_anonymous(self):
        test_user_block_mastery_level = self.test_block.get_mastery_level(self.test_user_anonymous)
        self.assertEquals(test_user_block_mastery_level, 0)

    def test_block_is_fully_learned_user_all_words_learned(self):
        test_user_block_fully_learned = self.test_block.is_fully_learned(self.test_user_all_words_learned)
        self.assertTrue(test_user_block_fully_learned)
    
    def test_block_is_fully_learned_user_no_words(self):
        test_user_block_fully_learned = self.test_block.is_fully_learned(self.test_user_no_words)
        self.assertFalse(test_user_block_fully_learned)
    
    def test_block_is_fully_learned_user_has_words(self):
        test_user_block_fully_learned = self.test_block.is_fully_learned(self.test_user_has_words)
        self.assertFalse(test_user_block_fully_learned)
    
    def test_block_is_fully_learned_user_anonymous(self):
        test_user_block_fully_learned = self.test_block.is_fully_learned(self.test_user_anonymous)
        self.assertFalse(test_user_block_fully_learned)
    

    def test_word_info_str(self):
        self.assertEquals(str(self.test_word_info_full), 'Test Word Full Name - Test Word Full Translation')
    
    def test_word_info_example_short_with_long_example(self):
        self.assertEquals(self.test_word_info_full.example_short(), 'Test Word Long ...')
    
    def test_word_info_example_short_with_short_example(self):
        self.assertEquals(self.test_word_info_short_example.example_short(), 'Short Example')

    def test_word_info_example_short_with_no_example(self):
        self.assertIsNone(self.test_word_info_no_example.example_short())
    
    def test_word_info_generate_three_options(self):
        self.test_word_info.generate_options(self.test_block)
        self.assertIsInstance(self.test_word_info.options, list)
        self.assertEquals(len(self.test_word_info.options), 4)
        for option in self.test_word_info.options:
            self.assertIn(option, WordInfo.objects.values_list('translation', flat=True))
    
    def test_word_info_generate_options_too_many_n_wrong(self):
        self.test_word_info.generate_options(self.test_block, n_wrong=100)
        self.assertIsInstance(self.test_word_info.options, list)
        self.assertEquals(len(self.test_word_info.options), WordInfo.objects.count())
    
    
    def test_user_word_str(self):
        self.assertEquals(str(self.test_user_word), 'test_user_has_words - Test Word')
    
    def test_user_word_mastery_level_is_one(self):
        self.assertEquals(self.test_user_word.mastery_level, 1)

    def test_user_word_mastery_level_is_zero(self):
        self.assertEquals(self.test_user_word2.mastery_level, 0)
    