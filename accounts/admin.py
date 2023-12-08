from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, CustomUserToken, MyProfile


class CustomUserAdmin(UserAdmin, admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'is_premium', 'date_joined', 'is_active']
    list_filter = ['is_premium', 'is_active', 'date_joined']
    sortable_by = ['username', 'is_premium', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_premium',)}),
    )


class CustomUserTokenAdmin(admin.ModelAdmin):
    model = CustomUserToken
    list_display = ['user', 'token', 'expire_date', 'is_expired']
    list_filter = ['user', 'expire_date']
    sortable_by = ['user', 'token', 'expire_date', 'is_expired']


class MyProfileAdmin(admin.ModelAdmin):
    model = MyProfile
    list_display = ['user', 'num_learned_words', 'experience']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(CustomUserToken, CustomUserTokenAdmin)
admin.site.register(MyProfile, MyProfileAdmin)
