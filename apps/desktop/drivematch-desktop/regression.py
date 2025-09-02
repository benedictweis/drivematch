import datetime

import numpy as np
from drivematch.types import ScoredCar
from scipy.optimize import curve_fit


def regression_line(
    scored_cars: list[ScoredCar], function_type: str
) -> tuple[list[datetime.datetime], list[float]]:
    today = datetime.datetime.now()

    # Prepare data for regression
    x_data = np.array(
        [
            (today - scored_car.car.first_registration).days / 365.25
            for scored_car in scored_cars
        ]
    )
    y_data = np.array([scored_car.car.price for scored_car in scored_cars])

    if len(x_data) <= 1:
        return

    # Define multiple depreciation functions for flexibility
    def linear_depreciation(x, a, b):
        return a - b * x

    def exponential_depreciation(x, a, b):
        return a * np.exp(-b * x)

    def power_law_depreciation(x, a, b):
        return a * (x**-b)

    def logarithmic_depreciation(x, a, b):
        return a - b * np.log(1 + x)

    def polynomial_2_depreciation(x, a, b, c):
        return a - b * x + c * (x**2)

    def polynomial_3_depreciation(x, a, b, c, d):
        return a - b * x + c * (x**2) + d * (x**3)

    def polynomial_4_depreciation(x, a, b, c, d, e):
        return a - b * x + c * (x**2) + d * (x**3) + e * (x**4)

    # Select the depreciation function based on the dropdown
    if function_type == "linear":
        depreciation_function = linear_depreciation
    elif function_type == "exponential":
        depreciation_function = exponential_depreciation
    elif function_type == "power_law":
        depreciation_function = power_law_depreciation
    elif function_type == "logarithmic":
        depreciation_function = logarithmic_depreciation
    elif function_type == "polynomial_2":
        depreciation_function = polynomial_2_depreciation
    elif function_type == "polynomial_3":
        depreciation_function = polynomial_3_depreciation
    elif function_type == "polynomial_4":
        depreciation_function = polynomial_4_depreciation

    params, _ = curve_fit(depreciation_function, x_data, y_data)

    # Generate points for the regression curve
    x_curve = np.linspace(x_data.min(), x_data.max(), 500)
    y_curve = np.array([depreciation_function(x_point, *params) for x_point in x_curve])
    x_curve = np.array([today - datetime.timedelta(days=x * 365.25) for x in x_curve])
    return x_curve, y_curve
