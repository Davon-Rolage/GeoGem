from collections import Counter
from datetime import datetime
import secrets

from django.db import models
from django.template.defaultfilters import slugify

from accounts.models import CustomUser

from .config import MASTERY_LEVELS, LEVEL_INCREMENT


class Block(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    theory = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.name)
        super(Block, self).save(*args, **kwargs)
        
    def get_mastery_level(self, user):
        if user.is_authenticated:
            block_user_words = UserWord.objects.filter(word__blocks=self, user=user)
            if block_user_words.count() > 0:
                num_block_words = WordInfo.objects.filter(blocks=self).count()
                
                block_mastery_levels = {}
                for level, threshold in MASTERY_LEVELS.items():
                    block_mastery_levels[level] = threshold * num_block_words
                
                user_points = 0
                for user_word in block_user_words:
                    user_points += user_word.points
                
                user_word_levels = Counter([user_word.mastery_level for user_word in block_user_words])
                for level in MASTERY_LEVELS.keys():
                    if level not in user_word_levels:
                        user_word_levels[level] = 0
                        
                numerator = sum(lvl * lvl_count for lvl, lvl_count in user_word_levels.items())
                denominator = num_block_words
                
                weighted_avg = numerator / denominator
                return weighted_avg

        return 0
    
    def is_fully_learned(self, user):
        if user.is_authenticated:
            block_words = WordInfo.objects.filter(blocks=self)
            block_user_words = UserWord.objects.filter(word__blocks=self, user=user)
            return len(block_words) == len(block_user_words)

        return False


class WordInfo(models.Model):
    name = models.CharField(max_length=100)
    transliteration = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    example = models.TextField(blank=True, null=True)
    example_image = models.ImageField(upload_to='images/word_example/', blank=True, null=True)
    audio = models.FileField(upload_to='audio/word_info/', blank=True, null=True)
    image = models.ImageField(upload_to='images/word_info/', blank=True, null=True)
    blocks = models.ManyToManyField(Block)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} - {self.translation}'
    
    def block_list(self):
        return ", ".join([block.slug for block in self.blocks.all()])
    
    def has_audio(self):
        return bool(self.audio)
    
    def example_short(self):
        example_length = len(self.example) if isinstance(self.example, str) else 0
        return self.example[:15] + '...' if example_length > 15 else self.example
    
    def generate_options(self, block, n_wrong=3):
        self.options = [self.translation]
        words = WordInfo.objects.filter(blocks=block).exclude(id=self.id)
        words = list(words.values_list('translation', flat=True))
        for _ in range(n_wrong):
            wrong_option = secrets.choice(words)
            self.options.append(wrong_option)
            words.remove(wrong_option)
            
        self.options = sorted(self.options, key=lambda x: secrets.randbits(32))


class UserWord(models.Model):
    word = models.ForeignKey(WordInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    mastery_level = models.PositiveBigIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user} - {self.word}'
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        self.mastery_level = max([level for level, threshold in MASTERY_LEVELS.items() if self.points >= threshold] or [0])
        super(UserWord, self).save(*args, **kwargs)

