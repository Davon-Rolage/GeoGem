from django.urls import path

from .utils import reset_test_block
from .views import *


urlpatterns = [
    path('', BlockListView.as_view(), name='learn'),
    path('about/', AboutView.as_view(), name='about'),
    path('my_words/', MyWordsListView.as_view(), name='user_words'),
    path('my_words/<slug:slug>/', UserBlockDetailView.as_view(), name='user_block_detail'),
    path('add_word_info/', AddWordInfoView.as_view(), name='add_word_info'),
    path('edit_word_info/', EditWordInfoView.as_view(), name='edit_word_info'),
    path('blocks_table/', EditBlocksView.as_view(), name='blocks_table'),
    path('reset_test_block/', reset_test_block, name='reset_test_block'),
    path('<slug:slug>/', BlockDetailView.as_view(), name='block_detail'),
    path('<slug:slug>/edit/', EditBlockDetailView.as_view(), name='block_edit'),
]
