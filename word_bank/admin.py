from django.contrib import admin
from word_bank.models import *


class BlockIsBasicListFilter(admin.SimpleListFilter):
    title = 'Block is basic'
    parameter_name = 'is_basic'
    
    def lookups(self, request, model_admin):
        return [
            ('basic', 'Basic'),
            ('not_basic', 'Advanced'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'basic':
            return queryset.filter(
                name__startswith='Basic'
            )
        if self.value() == 'not_basic':
            return queryset.exclude(
                name__startswith='Basic'
            )

class AdvancedUserWordMasteryLevelListFilter(admin.SimpleListFilter):
    title = 'Mastery level'
    parameter_name = 'mastery_level'
    
    def lookups(self, request, model_admin):
        # Only show mastery levels that UserWords have
        exp_levels = [str(i) for i in range(7)]
        qs = model_admin.get_queryset(request)
        for i, exp_level in enumerate(EXP_NEEDED_BY_WORD_MASTERY_LEVEL):
            try:
                if qs.filter(points__gte=exp_level, points__lt=EXP_NEEDED_BY_WORD_MASTERY_LEVEL[i+1]).exists():
                    yield (exp_levels[i], exp_levels[i])

            except IndexError:
                pass
    
    def queryset(self, request, queryset):
        if self.value():
            level = int(self.value())
            max_mastery_level = len(EXP_NEEDED_BY_WORD_MASTERY_LEVEL) - 1
            
            if level < max_mastery_level:
                queryset = queryset.filter(
                    points__gte=EXP_NEEDED_BY_WORD_MASTERY_LEVEL[level],
                    points__lt=EXP_NEEDED_BY_WORD_MASTERY_LEVEL[level+1]
                )
            elif level == max_mastery_level:
                queryset = queryset.filter(
                    points__gte=EXP_NEEDED_BY_WORD_MASTERY_LEVEL[level]
                )   
        return queryset


class BlockAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'added_at', 'updated_at']
    list_filter = [BlockIsBasicListFilter,'added_at', 'updated_at']
    sortable_by = ['name', 'added_at', 'updated_at']
    ordering = ['-updated_at']
    

class WordInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'transliteration', 'translation', 'has_audio', 'example_short', 'added_at']
    list_filter = [
        ('image', admin.EmptyFieldListFilter),
        ('audio', admin.EmptyFieldListFilter),
        ('example', admin.EmptyFieldListFilter),
        ('example_image', admin.EmptyFieldListFilter),
        'blocks'
    ]
    sortable_by = ['name', 'translation', 'blocks', 'added_at']
    

class UserWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'user', 'points', 'mastery_level', 'updated_at']
    sortable_by = ['word', 'user', 'points', 'mastery_level', 'updated_at']
    list_filter = [AdvancedUserWordMasteryLevelListFilter, 'user', 'updated_at']
    ordering = ['-updated_at', 'user', 'points']


admin.site.register(Block, BlockAdmin)
admin.site.register(WordInfo, WordInfoAdmin)
admin.site.register(UserWord, UserWordAdmin)
