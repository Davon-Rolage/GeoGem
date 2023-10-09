from django.db import models
from django.template.defaultfilters import slugify


class Quiz(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=False, unique=True)
    quiz_type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    num_questions = models.PositiveIntegerField(default=10)
    added_at = models.DateTimeField(auto_now_add=True)

    def __save__(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Quiz, self).save(*args, **kwargs)
        