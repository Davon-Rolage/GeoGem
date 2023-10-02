from django.urls import path
from word_bank.views import *


urlpatterns = [
    path('', BlockListView.as_view(), name='learn'),
    path('<slug:slug>/', BlockDetailView.as_view(), name='block_detail'),
    
]
