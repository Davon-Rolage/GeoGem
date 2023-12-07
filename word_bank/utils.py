from collections import Counter


EXP_NEEDED_BY_WORD_MASTERY_LEVEL = [0, 1, 5, 15, 35, 70, 100]

def get_ml_chart_data(mastery_levels=None):
    mastery_levels_dct = Counter(mastery_levels)
    mastery_levels_dct.update({level: 0 for level in range(len(EXP_NEEDED_BY_WORD_MASTERY_LEVEL)) if level not in EXP_NEEDED_BY_WORD_MASTERY_LEVEL})
    x, y = zip(*sorted(mastery_levels_dct.items()))
    return {'x': list(x), 'y': list(y)}
    