from collections import Counter
import secrets

from django.db import models
from django.template.defaultfilters import slugify

from accounts.models import CustomUser

from .config import MASTERY_LEVELS


class Block(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    theory = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Block, self).save(*args, **kwargs)
        
    def get_mastery_level(self, user):
        if user.is_authenticated:
            block_words = UserWord.objects.filter(word__blocks=self, user=user)
            mastery_levels = dict(Counter([word.mastery_level for word in block_words]))
            for level in MASTERY_LEVELS.keys():
                if level not in mastery_levels:
                    mastery_levels[level] = 0

            if len(block_words) > 0:
                numerator = sum(k * v for k, v in mastery_levels.items())
                denominator = sum(mastery_levels.values())
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
    
    def __str__(self):
        return f'{self.user} - {self.word}'
    
    def save(self, *args, **kwargs):
        self.mastery_level = max([level for level, threshold in MASTERY_LEVELS.items() if self.points >= threshold] or [0])
        super(UserWord, self).save(*args, **kwargs)

