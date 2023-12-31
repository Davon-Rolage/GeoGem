from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from word_bank.config import LEVEL_XP, LEVEL_XP_INCREMENT, MAX_LEVEL


class CustomUser(AbstractUser):
    is_premium = models.BooleanField(
        default=False,
        help_text='Designates whether the user is a premium user.'
    )
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.get_username()
    
    def save(self, *args, **kwargs):
        if self.is_staff or self.is_superuser:
            self.is_active = True
            
        super().save(*args, **kwargs)
   

class CustomUserTokenType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class CustomUserToken(models.Model):    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    token_type = models.ForeignKey(CustomUserTokenType, on_delete=models.CASCADE)
    expire_date = models.DateTimeField(verbose_name="Token expire date")
    token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.user.get_username() + ' - ' + self.token
    
    def save(self, *args, **kwargs):
        if not self.expire_date:
            self.expire_date = timezone.now() + timezone.timedelta(days=3)
        super().save(*args, **kwargs)

    
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Profile {self.user.get_username()}'
    
    def save(self, *args, **kwargs):
        self.experience = max(self.experience, 0)
        super().save(*args, **kwargs)
        
    @property
    def num_learned_words(self):
        return self.user.userword_set.count()

    @property
    def level(self):
        for level, xp in LEVEL_XP.items():
            if self.experience < xp:
                return level - 1
                
        return MAX_LEVEL
                
    @property
    def level_progress(self):
        if self.level < MAX_LEVEL:
            return (self.experience - LEVEL_XP[self.level]) / LEVEL_XP_INCREMENT[self.level+1]
        
        return 1

    @property
    def xp_to_next_level(self):
        if self.level < MAX_LEVEL:
            return LEVEL_XP[self.level + 1] - self.experience

        return 0
