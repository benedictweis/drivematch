import pytest

from drivematch._internal.analysis import CarsAnalyzer


@pytest.mark.unit
def test_should_analyze_cars_data() -> None:
    analyzer = CarsAnalyzer()

    assert analyzer is not None
