from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from word_bank.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    path('', include('accounts.urls')),
    path('learn/', include('word_bank.urls')),
    path('quizzer/', include('quizzer.urls')),
    path('accounts/', include('accounts.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
