import numpy as np


def linear_depreciation(x, a, b):  # noqa: ANN001, ANN202
    return a - b * x


def exponential_depreciation(x, a, b):  # noqa: ANN001, ANN202
    return a * np.exp(-b * x)


def power_law_depreciation(x, a, b):  # noqa: ANN001, ANN202
    return a * (x**-b)


def logarithmic_depreciation(x, a, b):  # noqa: ANN001, ANN202
    return a - b * np.log(1 + x)


def polynomial_2_depreciation(x, a, b, c):  # noqa: ANN001, ANN202
    return a - b * x + c * (x**2)


def polynomial_3_depreciation(x, a, b, c, d):  # noqa: ANN001, ANN202
    return a - b * x + c * (x**2) + d * (x**3)


def polynomial_4_depreciation(x, a, b, c, d, e):  # noqa: ANN001, ANN202, PLR0913
    return a - b * x + c * (x**2) + d * (x**3) + e * (x**4)
