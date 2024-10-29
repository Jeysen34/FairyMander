import pytest
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
from fairness import (
    calc_avg_polsby_popper,
    calc_avg_reock,
    calc_efficiency_gap,
    calc_mean_median_difference,
    calc_lobsided_margins,
    calc_dissimilarity_index,
    get_metric_dict
)

def create_test_map():
    # Create a simple GeoDataFrame with one district
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    data = {
        'District': [1],
        'geometry': [poly],
        'party_rep': [600],
        'party_dem': [400],
        'eth1_eur': [800],
        'eth1_aa': [100],
        'eth1_esa': [50],
        'eth1_hisp': [30],
        'eth1_oth': [20]
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")

def create_multiple_districts_map():
    # Create a GeoDataFrame with multiple districts
    polys = [
        Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),
        Polygon([(2, 0), (4, 0), (4, 2), (2, 2)]),
        Polygon([(0, 2), (2, 2), (2, 4), (0, 4)]),
        Polygon([(2, 2), (4, 2), (4, 4), (2, 4)])
    ]
    data = {
        'District': [1, 2, 3, 4],
        'geometry': polys,
        'party_rep': [600, 400, 300, 700],
        'party_dem': [400, 600, 700, 300],
        'eth1_eur': [800, 700, 900, 600],
        'eth1_aa': [100, 150, 50, 200],
        'eth1_esa': [50, 30, 70, 20],
        'eth1_hisp': [30, 40, 20, 10],
        'eth1_oth': [20, 80, 10, 70]
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")

def test_calc_avg_polsby_popper():
    test_map = create_test_map()
    result = calc_avg_polsby_popper(test_map)
    assert isinstance(result, float)
    assert 0 <= result <= 1

def test_calc_avg_reock():
    test_map = create_test_map()
    result = calc_avg_reock(test_map)
    assert isinstance(result, float)
    assert 0 <= result <= 1

def test_calc_efficiency_gap():
    test_map = create_multiple_districts_map()
    result = calc_efficiency_gap(test_map)
    assert isinstance(result, float)
    assert -100 <= result <= 100

def test_calc_mean_median_difference():
    test_map = create_multiple_districts_map()
    result = calc_mean_median_difference(test_map)
    assert isinstance(result, float)
    assert -100 <= result <= 100

def test_calc_lobsided_margins():
    test_map = create_multiple_districts_map()
    result = calc_lobsided_margins(test_map)
    assert isinstance(result, float)
    assert -100 <= result <= 100

def test_calc_dissimilarity_index():
    test_map = create_multiple_districts_map()
    result = calc_dissimilarity_index(test_map)
    expected_keys = {'eth1_hisp', 'eth1_aa', 'eth1_esa', 'eth1_oth'}
    assert isinstance(result, dict)
    assert set(result.keys()) == expected_keys
    for value in result.values():
        assert isinstance(value, float)
        assert 0 <= value <= 1

def test_get_metric_dict():
    test_map = create_multiple_districts_map()
    result = get_metric_dict(test_map)
    expected_keys = {
        'Avg Polsby-Popper',
        'Avg Reock',
        'Efficiency Gap',
        'Mean Median Difference',
        'Lobsided Margin',
        'Dissimilarity Indices'
    }
    assert isinstance(result, dict)
    assert set(result.keys()) == expected_keys
