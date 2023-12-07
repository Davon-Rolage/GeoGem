import math
from pprint import pprint


def calculate_level_increment(level):
    k = 24.3
    b = -9.8
    result = k * math.log(level) + b
    return max(1, math.ceil(result))

    
MAX_LEVEL = 100
LEVEL_XP_INCREMENT = [calculate_level_increment(level) for level in range(1, MAX_LEVEL+1)]
LEVEL_XP = {level: sum(LEVEL_XP_INCREMENT[:level]) for level in range(1, len(LEVEL_XP_INCREMENT)+1)}

LEVEL_XP_INCREMENT.insert(0, 0)
LEVEL_XP = {0: 0, **LEVEL_XP}

if __name__ == '__main__':
    pivot_xp_table = {level: (LEVEL_XP[level], LEVEL_XP_INCREMENT[level]) for level in LEVEL_XP.keys()}
    print('level: (total_xp_to_this_level, incremental_xp_to_this_level)')
    pprint(pivot_xp_table)
