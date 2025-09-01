import pytest
from drivematch.analysis import CarsAnalyzer

@pytest.mark.unit
def test_should_analyze_cars_data():
    analyzer = CarsAnalyzer()

    assert analyzer is not None