import secrets

from django.db import models
from django.template.defaultfilters import slugify

from accounts.models import CustomUser

from .config import MASTERY_LEVELS


class Block(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Block, self).save(*args, **kwargs)
        
    def get_mastery_level(self):
        block_words = UserWord.objects.filter(word__blocks=self)
        total_mastery_level = 0
        total_mastery_level_pct = 0
        
        for level in MASTERY_LEVELS.values():
            total_mastery_level += level * len(block_words.filter(mastery_level=level))
        total_mastery_level /= len(block_words)
        total_mastery_level_pct /= len(MASTERY_LEVELS) * 100
        return total_mastery_level, total_mastery_level_pct


class WordInfo(models.Model):
    name = models.CharField(max_length=100)
    transliteration = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    audio = models.FileField(upload_to='audio/', blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    blocks = models.ManyToManyField(Block)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name} - {self.translation}'
    
    def generate_options(self, block, n_wrong):
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
        self.mastery_level = MASTERY_LEVELS.get(self.points, 0)
        super(UserWord, self).save(*args, **kwargs)

