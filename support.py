import math

import numpy as np


def get_exp(value):
    return -1 * math.log(1 - np.random.uniform()) / value


def bool_to_int(value):
    if value:
        return 1
    else:
        return 0
