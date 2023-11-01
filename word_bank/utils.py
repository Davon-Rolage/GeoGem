from collections import Counter

from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy

from .config import MASTERY_LEVELS


def get_ml_chart_data(mastery_levels=None):
    mastery_levels_dct = dict(Counter(mastery_levels))
    for level in MASTERY_LEVELS.keys():
        if level not in mastery_levels_dct:
            mastery_levels_dct[level] = 0

    mastery_levels_dct = dict(sorted(mastery_levels_dct.items()))
    x = sorted(list(mastery_levels_dct.keys()))
    y = list(mastery_levels_dct.values())
    return {'x': x, 'y': y}


def staff_member_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=reverse_lazy('login')
    )
    return decorated_view_func(view_func)
