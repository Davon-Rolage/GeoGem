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

    path('premium/', PremiumView.as_view(), name='premium'),
    path('get-premium/', GetPremiumView.as_view(), name='get_premium'),
    path('cancel-premium/', CancelPremiumView.as_view(), name='cancel_premium'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
