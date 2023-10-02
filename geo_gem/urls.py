from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('learn/', include('word_bank.urls')),
    path('quizzer/', include('quizzer.urls')),
]
