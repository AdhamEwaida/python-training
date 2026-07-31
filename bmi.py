import math


def bmi_calculator(height: float, weight: float) -> float:
    """Calculate BMI from height in meters and weight in kilograms."""
    if isinstance(height, bool) or not isinstance(height, (int, float)):
        raise TypeError("height must be a number")

    if isinstance(weight, bool) or not isinstance(weight, (int, float)):
        raise TypeError("weight must be a number")

    if not math.isfinite(height) or height <= 0:
        raise ValueError("height must be a positive finite number")

    if not math.isfinite(weight) or weight <= 0:
        raise ValueError("weight must be a positive finite number")

    return weight / height**2
