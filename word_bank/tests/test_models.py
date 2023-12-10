from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from word_bank.models import Block, UserWord, WordInfo


class BlockModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        
        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_block_custom_slug = Block.objects.create(
            name='Test Slug', slug='test_custom_slug'
        )
        cls.test_block_with_empty_name = Block.objects.create(name=' ')

        test_users = [
            cls.User(username=f'test_user_{suffix}', is_active=True) for suffix in (
                'no_words', 'has_words', 'all_words_learned'
            )
        ]
        cls.User.objects.bulk_create(test_users)
        cls.test_user_no_words, cls.test_user_has_words, cls.test_user_all_words_learned = test_users

        test_word_infos = [
            WordInfo(),
            WordInfo(name='Test Word'),
            WordInfo(name='Test Word 2'),
            WordInfo(
                name='Test Word Full Name',
                translation='Test Word Full Translation',
                example='Test Word Long Example'
            ),
        ]
        WordInfo.objects.bulk_create(test_word_infos)
        cls.test_block.wordinfo_set.add(*test_word_infos)

        cls.test_word_info_no_example = test_word_infos[0]
        cls.test_word_info = test_word_infos[1]
        cls.test_word_info2 = test_word_infos[2]
        cls.test_word_info_full = test_word_infos[3]
        
        user_word_objects = [
            UserWord(user=cls.test_user_has_words, word=cls.test_word_info, points=1),
            UserWord(user=cls.test_user_has_words, word=cls.test_word_info2),
        ] + [
            UserWord(
                user=cls.test_user_all_words_learned,
                word=word_info,
                points=1
            ) for word_info in test_word_infos
        ]
        UserWord.objects.bulk_create(user_word_objects)
        
    def test_block_str(self):
        self.assertEqual(str(self.test_block), 'Test Block')

    def test_block_default_slug_is_assigned_on_save(self):
        self.assertEqual(self.test_block.slug, 'test-block')
        
    def test_block_custom_slug_is_preserved_on_save(self):
        self.assertEqual(self.test_block_custom_slug.slug, 'test_custom_slug')

    def test_block_default_slug_is_assigned_on_save(self):
        self.assertEqual(self.test_block_with_empty_name.name, 'New Block')
        self.assertEqual(self.test_block_with_empty_name.slug, 'new-block')
    
    def test_block_get_mastery_level_user_has_words(self):
        test_user_block_mastery_level = self.test_block.get_mastery_level(self.test_user_has_words)
        self.assertEqual(test_user_block_mastery_level, 0.25)
    
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
    @classmethod
    def setUpTestData(cls):
        cls.test_block = Block.objects.create(name='Test Block')
        test_word_infos = [
            WordInfo(name='Test Word'),
            WordInfo(name='Test Word 2'),
            WordInfo(example='Short Example'),
            WordInfo(name='Test Word Full Name', translation='Test Word Full Translation', example='Test Word Long Example'),
            WordInfo(),
        ]
        WordInfo.objects.bulk_create(test_word_infos)
            
        cls.test_word_info = test_word_infos[0]
        cls.test_word_info2 = test_word_infos[1]
        cls.test_word_info_short_example = test_word_infos[2]
        cls.test_word_info_full = test_word_infos[3]
        cls.test_word_info_no_example = test_word_infos[4]

        WordInfo.blocks.through.objects.bulk_create([
            WordInfo.blocks.through(wordinfo_id=word_info.id, block_id=cls.test_block.id) for word_info in test_word_infos
        ])

    def test_word_info_str(self):
        self.assertEqual(str(self.test_word_info_full), 'Test Word Full Name - Test Word Full Translation')
    
    def test_word_info_example_short_with_long_example(self):
        self.assertEqual(self.test_word_info_full.example_short(), 'Test Word Long ...')
    
    def test_word_info_example_short_with_short_example(self):
        self.assertEqual(self.test_word_info_short_example.example_short(), 'Short Example')

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
    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()
        cls.test_block = Block.objects.create(name='Test Block')
        cls.test_user = cls.User.objects.create_user(
            username='test_user', password='test_password', is_active=True
        )
        for i in range(2):
            word = WordInfo.objects.create(name=f'Test Word {i+1}')
            word.blocks.add(cls.test_block)
        cls.test_word_info, cls.test_word_info2 = WordInfo.objects.all()

        cls.test_user_word = UserWord.objects.create(
            user=cls.test_user, word=cls.test_word_info, points=1
        )
        cls.test_user_word2 = UserWord.objects.create(user=cls.test_user, word=cls.test_word_info2)
    
    def test_user_word_str(self):
        self.assertEqual(str(self.test_user_word), 'test_user - Test Word 1')
    
    def test_user_word_mastery_level_is_one(self):
        self.assertEqual(self.test_user_word.mastery_level, 1)

    def test_user_word_mastery_level_is_zero(self):
        self.assertEqual(self.test_user_word2.mastery_level, 0)
    