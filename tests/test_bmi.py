import pytest

from bmi import bmi_calculator


@pytest.mark.parametrize(
    ("height", "weight", "expected"),
    [
        (1.75, 70, 22.8571428571),
        (1.60, 50, 19.53125),
        (2, 100, 25),
    ],
)
def test_bmi_calculator_returns_expected_value(height, weight, expected):
    assert bmi_calculator(height, weight) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("height", "weight"),
    [
        (0, 70),
        (-1.75, 70),
        (float("inf"), 70),
        (float("nan"), 70),
        (1.75, 0),
        (1.75, -70),
        (1.75, float("inf")),
        (1.75, float("nan")),
    ],
)
def test_bmi_calculator_rejects_non_positive_or_non_finite_values(height, weight):
    with pytest.raises(ValueError):
        bmi_calculator(height, weight)


@pytest.mark.parametrize(
    ("height", "weight"),
    [
        ("1.75", 70),
        (None, 70),
        (True, 70),
        (1.75, "70"),
        (1.75, None),
        (1.75, False),
    ],
)
def test_bmi_calculator_rejects_non_numeric_values(height, weight):
    with pytest.raises(TypeError):
        bmi_calculator(height, weight)
