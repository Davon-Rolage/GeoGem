from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, MyProfile


class CustomUserAdmin(UserAdmin, admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'is_premium', 'date_joined']
    list_filter = ['is_premium', 'date_joined']
    sortable_by = ['username', 'is_premium', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_premium',)}),
    )


class MyProfileAdmin(admin.ModelAdmin):
    model = MyProfile
    list_display = ['user', 'num_learned_words', 'experience']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MyProfile, MyProfileAdmin)
