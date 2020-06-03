from math import factorial


def num_combinations(total, selected):
    return int(factorial(total)/(factorial(selected)*factorial(total-selected)))
