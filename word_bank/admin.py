from django.contrib import admin
from word_bank.models import *


class BlockAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'added_at', 'updated_at']
    list_filter = ['added_at', 'updated_at']
    sortable_by = ['name', 'added_at', 'updated_at']
    ordering = ['-updated_at']
    

class WordInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'transliteration', 'translation', 'block_list', 'has_audio', 'example_short', 'added_at']
    list_filter = ['blocks']
    sortable_by = ['name', 'translation', 'blocks', 'added_at']
    

class UserWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'user', 'points', 'mastery_level', 'updated_at']
    list_filter = ['mastery_level', 'user', 'points', 'updated_at']
    sortable_by = ['word', 'user', 'points', 'mastery_level', 'updated_at']
    ordering = ['-updated_at', 'user', 'points']


admin.site.register(Block, BlockAdmin)
admin.site.register(WordInfo, WordInfoAdmin)
admin.site.register(UserWord, UserWordAdmin)
