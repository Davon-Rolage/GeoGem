from django.contrib import admin
from word_bank.models import *


class BlockAdmin(admin.ModelAdmin):
    list_display = ['name', 'added_at', 'updated_at']
    list_filter = ['added_at', 'updated_at']
    sortable_by = ['name', 'added_at', 'updated_at']
    

class WordInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'transliteration', 'translation', 'added_at']
    list_filter = ['blocks']
    sortable_by = ['name', 'translation', 'blocks', 'added_at']


class UserWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'user', 'points', 'mastery_level']
    list_filter = ['word', 'user', 'points', 'mastery_level']
    sortable_by = ['word', 'user', 'points', 'mastery_level']


admin.site.register(Block)
admin.site.register(WordInfo, WordInfoAdmin)
admin.site.register(UserWord, UserWordAdmin)
admin.site.register(QuizResult)

