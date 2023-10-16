from django.urls import path
from word_bank.views import *


urlpatterns = [
    path('', BlockListView.as_view(), name='learn'),
    path('my_words/', MyWordsListView.as_view(), name='my_words'),
    path('blocks_table/', EditBlocksView.as_view(), name='blocks_table'),
    path('<slug:slug>/', BlockDetailView.as_view(), name='block_detail'),
    path('<slug:slug>/edit/', EditBlockDetailView.as_view(), name='block_edit'),
]
