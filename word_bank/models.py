from django.db import models
from accounts.models import CustomUser
from django.template.defaultfilters import slugify
import secrets


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
    points = models.IntegerField(default=0)
    mastery_level = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user} - {self.name}'


class QuizResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    word = models.ForeignKey(WordInfo, on_delete=models.CASCADE)
    correct = models.BooleanField()
    


