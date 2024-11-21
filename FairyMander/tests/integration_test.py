
import pytest
from unittest.mock import patch, MagicMock
import geopandas as gpd
from os import path
from gerrychain import GeographicPartition
from fairymander.generator import DistrictGenerator
from fairymander.data import num_districts, epsg

@pytest.mark.parametrize(
    "prefix, deviation, steps, num_maps, opt_metric_flag",
    [
        # Standard random partition - compact
        ("az", 0.05, 1000, 3, "compact"),
        # Standard random partition - competitiveness
        ("az", 0.05, 1000, 3, "competitiveness"),
        # Random partition with low deviation boundary value
        ("az", 0.008, 1000, 3, "compact"),
        # Random partition on state with islands
        ("ma", 0.05, 1000, 3, "compact"),
    ]
)
def test_get_random_partition(prefix, deviation, steps, num_maps, opt_metric_flag):
    """
    Test the _get_random_partition method with various scenarios.

    Parameters:
    - prefix: str - State abbreviation.
    - deviation: float - Population deviation.
    - steps: int - Number of steps for the algorithm.
    - num_maps: int - Number of maps to generate.
    - opt_metric_flag: str - Optimization metric ("compact" or "competitiveness").
    """
    # Initialize the DistrictGenerator
    district_gen = DistrictGenerator(prefix, deviation, steps, num_maps, opt_metric_flag)

    # Generate the random partition
    partition = district_gen._get_random_partition()

    # Assertions
    assert isinstance(partition, GeographicPartition), "Partition is not a GeographicPartition instance"
    assert "population" in partition.updaters, "Partition is missing 'population' updater"
    assert "cut_edges" in partition.updaters, "Partition is missing 'cut_edges' updater"

    if opt_metric_flag == "compact":
        assert "polsby-popper" in partition.updaters, "'polsby-popper' updater missing for compact metric"
    else:
        assert "election" in partition.updaters, "'election' updater missing for competitiveness metric"

    # Check that the population deviation is within the specified range
    populations = partition["population"]
    total_population = sum(populations.values())
    ideal_population = total_population / len(partition.parts)
    max_population = (1 + deviation) * ideal_population
    min_population = (1 - deviation) * ideal_population

    for district, pop in populations.items():
        assert min_population <= pop <= max_population, f"District {district} population out of bounds"
