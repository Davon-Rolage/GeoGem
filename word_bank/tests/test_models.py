from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from word_bank.models import Block, WordInfo


class BlockModelTestCase(TestCase):
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        

        test_blocks = Block.objects.all()
        cls.test_block = test_blocks.first()
        cls.test_block_custom_slug = test_blocks.get(name='Test Block Custom Slug')
        cls.test_block_with_empty_name = test_blocks.create(name=' ')
        cls.test_block_default_slug = Block.objects.create(name='Test Block Default Slug')

        test_users = cls.User.objects.all()
        cls.test_user_no_words = test_users.get(username='test_user_no_words')
        cls.test_user_has_words = test_users.get(username='test_user_has_words')
        cls.test_user_all_words_learned = test_users.get(username='test_user_all_words_learned')
        
    def test_block_str(self):
        self.assertEqual(str(self.test_block_default_slug), 'Test Block Default Slug')

    def test_block_default_slug_is_assigned_on_save(self):
        self.assertEqual(self.test_block_default_slug.slug, 'test-block-default-slug')
        
    def test_block_custom_slug_is_preserved_on_save(self):
        self.assertEqual(self.test_block_custom_slug.slug, 'test_custom_slug')

    def test_block_default_slug_is_assigned_on_save(self):
        self.assertEqual(self.test_block_with_empty_name.name, 'New Block')
        self.assertEqual(self.test_block_with_empty_name.slug, 'new-block')
    
    def test_block_get_mastery_level_user_has_words(self):
        test_user_block_mastery_level = self.test_block.get_mastery_level(self.test_user_has_words)
        self.assertEqual(test_user_block_mastery_level, 0.2)
    
    def test_block_get_mastery_level_user_no_words(self):
        test_user_block_mastery_level = self.test_block.get_mastery_level(self.test_user_no_words)
        self.assertEqual(test_user_block_mastery_level, 0)
    
    def test_block_get_mastery_level_user_anonymous(self):
        test_user_block_mastery_level = self.test_block.get_mastery_level(AnonymousUser())
        self.assertEqual(test_user_block_mastery_level, 0)

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
        test_user_block_fully_learned = self.test_block.is_fully_learned(AnonymousUser())
        self.assertFalse(test_user_block_fully_learned)


class WordInfoModelTestCase(TestCase):
    fixtures = ['test_users.json', 'test_blocks.json', 'test_word_infos.json']
    
    @classmethod
    def setUpTestData(cls):
        cls.test_block = Block.objects.first()
        
        test_word_infos = WordInfo.objects.all()
        cls.test_word_info, cls.test_word_info2 = test_word_infos[:2]
        cls.test_word_info_short_example = test_word_infos.get(example='short_example')
        cls.test_word_info_full = test_word_infos.get(example='text_word_long_example')
        cls.test_word_info_no_example = test_word_infos.get(name='test_word_no_example')

    def test_word_info_str(self):
        self.assertEqual(str(self.test_word_info_full), 'test_word_long_example - test_transl_long_example')
    
    def test_word_info_example_short_with_long_example(self):
        self.assertEqual(self.test_word_info_full.example_short(), 'text_word_long_...')
    
    def test_word_info_example_short_with_short_example(self):
        self.assertEqual(self.test_word_info_short_example.example_short(), 'short_example')

    def test_word_info_example_short_with_no_example(self):
        self.assertIsNone(self.test_word_info_no_example.example_short())
    
    def test_word_info_generate_three_options(self):
        self.test_word_info.generate_options(self.test_block)

        self.assertIsInstance(self.test_word_info.options, list)
        self.assertEqual(len(self.test_word_info.options), 4)
        for option in self.test_word_info.options:
            self.assertIn(option, WordInfo.objects.values_list('translation', flat=True))
    
    def test_word_info_generate_options_too_many_n_wrong(self):
        self.test_word_info.generate_options(self.test_block, n_wrong=100)
        
        self.assertIsInstance(self.test_word_info.options, list)
        self.assertEqual(len(self.test_word_info.options), WordInfo.objects.count())


class UserWordModelTestCase(TestCase):
    fixtures = [
        'test_users.json', 'test_blocks.json',
        'test_word_infos.json', 'test_user_words.json'
    ]
    
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.test_user = cls.User.objects.first()
        cls.test_user_word, cls.test_user_word2 = cls.test_user.userword_set.all()[:2]
    
    def test_user_word_str(self):
        self.assertEqual(str(self.test_user_word), 'test_user - test_word')
    
    def test_user_word_mastery_level_is_one(self):
        self.assertEqual(self.test_user_word.mastery_level, 1)

    def test_user_word_mastery_level_is_zero(self):
        self.assertEqual(self.test_user_word2.mastery_level, 0)
    