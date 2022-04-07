import math

import numpy as np


def get_exp(value):
    return -1 * math.log(1 - np.random.uniform()) / value


def bool_to_int(value):
    if value:
        return 1
    else:
        return 0


def count_all_elements(lst):
    result = 0

    for element in lst:
        if isinstance(element, list):
            for _ in element:
                result += 1
        else:
            result += 1

    return result


def get_avg_over_array(lst):
    return sum(lst) / len(lst)
