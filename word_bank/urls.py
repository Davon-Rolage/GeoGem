from django.urls import path
from word_bank.views import *


urlpatterns = [
    path('', BlockListView.as_view(), name='learn'),
    path('about/', AboutView.as_view(), name='about'),
    path('my_words/', MyWordsListView.as_view(), name='user_words'),
    path('my_words/<slug:slug>/', UserBlockDetailView.as_view(), name='user_block_detail'),
    path('blocks_table/', EditBlocksView.as_view(), name='blocks_table'),
    path('<slug:slug>/', BlockDetailView.as_view(), name='block_detail'),
    path('<slug:slug>/edit/', EditBlockDetailView.as_view(), name='block_edit'),
    
]
