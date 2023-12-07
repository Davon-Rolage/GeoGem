from django.contrib.auth.models import AbstractUser
from django.db import models

from word_bank.config import LEVEL_XP, LEVEL_XP_INCREMENT


class CustomUser(AbstractUser):
    is_premium = models.BooleanField(
        default=False,
        help_text='Designates whether the user is a premium user.'
    )
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    
    
class MyProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    num_learned_words = models.IntegerField(default=0)
    experience = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    @property
    def level(self):
        for level, xp in LEVEL_XP.items():
            if self.experience < xp:
                return level - 1
                
    @property
    def level_progress(self):
        return (self.experience - LEVEL_XP[self.level]) / LEVEL_XP_INCREMENT[self.level+1]

    @property
    def xp_to_next_level(self):
        return LEVEL_XP[self.level + 1] - self.experience
