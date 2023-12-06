from collections import Counter

from .config import MASTERY_LEVELS


def get_ml_chart_data(mastery_levels=None):
    mastery_levels_dct = Counter(mastery_levels)
    mastery_levels_dct.update({level: 0 for level in MASTERY_LEVELS.keys() if level not in mastery_levels_dct})
    x, y = zip(*sorted(mastery_levels_dct.items()))
    return {'x': list(x), 'y': list(y)}
    