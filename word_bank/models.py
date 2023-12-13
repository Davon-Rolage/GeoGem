import secrets
from bisect import bisect_right
from collections import Counter
from datetime import datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from accounts.models import CustomUser

from .utils import EXP_NEEDED_BY_WORD_MASTERY_LEVEL


class Block(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    theory = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_visible = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('block_detail', kwargs={'slug': self.slug})
        
    def save(self, *args, **kwargs):
        self.name = self.name.strip() or 'New Block'
        self.slug = self.slug or slugify(self.name)
        super().save(*args, **kwargs)
    
        
    def get_mastery_level(self, user):
        if user.is_authenticated:
            block_user_words = UserWord.objects.filter(word__blocks=self, user=user)
            if block_user_words.exists():
                user_word_levels = Counter(user_word.mastery_level for user_word in block_user_words)
                user_word_levels.update({level: 0 for level in range(len(EXP_NEEDED_BY_WORD_MASTERY_LEVEL)) if level not in user_word_levels})
                
                numerator = sum(lvl * lvl_count for lvl, lvl_count in user_word_levels.items())

                num_block_words = WordInfo.objects.filter(blocks=self).count()
                denominator = num_block_words
                weighted_avg = numerator / denominator
                return weighted_avg

        return 0
    
    def is_fully_learned(self, user) -> bool:
        if user.is_authenticated:
            block_words_length = WordInfo.objects.filter(blocks=self).count()
            block_user_words_length = UserWord.objects.filter(word__blocks=self, user=user).count()
            return block_words_length == block_user_words_length

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
    updated_at = models.DateTimeField(auto_now=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} - {self.translation}'
    
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
            try:
                wrong_option = secrets.choice(words)
                self.options.append(wrong_option)
                words.remove(wrong_option)
            except IndexError:
                break
            
        self.options = sorted(self.options, key=lambda x: secrets.randbits(32))
        return self.options


class UserWord(models.Model):
    word = models.ForeignKey(WordInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user} - {self.word.name}'
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(UserWord, self).save(*args, **kwargs)
    
    @property
    def mastery_level(self):
        level = bisect_right(EXP_NEEDED_BY_WORD_MASTERY_LEVEL, self.points) - 1
        return level
