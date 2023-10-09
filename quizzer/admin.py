from django.contrib import admin
from .models import Quiz


class QuizAdmin(admin.ModelAdmin):
    list_display = ['name', 'quiz_type', 'description', 'added_at']
    list_filter = ['quiz_type', 'added_at']

admin.site.register(Quiz, QuizAdmin)
