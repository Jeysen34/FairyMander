import pytest
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
from fairymander.fairness import (
    calc_avg_polsby_popper,
    calc_avg_reock,
    calc_efficiency_gap,
    calc_mean_median_difference,
    calc_lopsided_margins,
    calc_dissimilarity_index,
    get_metric_dict,
    compare_maps
)

@pytest.fixture
def single_district_map():
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

@pytest.fixture
def multiple_districts_map():
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
        'eth2_81': [20, 10, 15, 25],
        'eth1_oth': [20, 80, 10, 70]
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")

@pytest.fixture
def map_a_metrics():
    return {
        'Avg Polsby-Popper': 0.75,
        'Avg Reock': 0.65,
        'Efficiency Gap': -2.0,
        'Mean Median Difference': -1.5,
        'Lopsided Margin': 4.0,
        'Dissimilarity Indices': {
            'eth1_aa': 0.20,
            'eth1_esa': 0.25,
            'eth1_hisp': 0.30,
            'eth2_81': 0.18,
            'eth1_oth': 0.22
        }
    }


@pytest.fixture
def map_b_metrics():
    return {
        'Avg Polsby-Popper': 0.60,
        'Avg Reock': 0.50,
        'Efficiency Gap': -3.5,
        'Mean Median Difference': -2.0,
        'Lopsided Margin': 4.0,
        'Dissimilarity Indices': {
            'eth1_aa': 0.25,
            'eth1_esa': 0.28,
            'eth1_hisp': 0.35,
            'eth2_81': 0.20,
            'eth1_oth': 0.20
        }
    }

def test_calc_avg_polsby_popper_one_district(single_district_map):
    district_area = single_district_map.loc[0, 'geometry'].area
    district_perimeter = single_district_map.loc[0, 'geometry'].length
    pp_score = (4 * np.pi) * (district_area / (district_perimeter ** 2))
    result = calc_avg_polsby_popper(single_district_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == pp_score
    assert 0 <= result <= 1

def test_calc_avg_polsby_popper_mult_districts(multiple_districts_map):
    pp_scores = []
    for index in range(4):
        district_area = multiple_districts_map.loc[index, 'geometry'].area
        district_perimeter = multiple_districts_map.loc[index, 'geometry'].length
        pp_score = (4 * np.pi) * (district_area / (district_perimeter ** 2))
        pp_scores.append(pp_score)
    pp_average = sum(pp_scores) / len(pp_scores)
    result = calc_avg_polsby_popper(multiple_districts_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == pp_average

def test_calc_avg_reock(single_district_map):
    district_area = single_district_map.loc[0, 'geometry'].area
    min_bounding_circle = single_district_map.minimum_bounding_circle()[0]
    min_bounding_circle_area = min_bounding_circle.area
    expected_reock_score = district_area / min_bounding_circle_area

    result = calc_avg_reock(single_district_map)

    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == expected_reock_score
    assert 0 <= result <= 1

def test_calc_avg_reock_multiple_districts(multiple_districts_map):
    # Calculate expected Reock score for multiple districts
    reock_scores = []
    min_bounding_circles = multiple_districts_map.minimum_bounding_circle()

    for index in range(len(multiple_districts_map)):
        district_area = multiple_districts_map.loc[index, 'geometry'].area
        min_bounding_circle_area = min_bounding_circles[index].area
        reock_scores.append(district_area / min_bounding_circle_area)

    expected_average_reock = sum(reock_scores) / len(reock_scores)

    # Calculate using the function
    result = calc_avg_reock(multiple_districts_map)

    # Assertions
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == expected_average_reock
    assert 0 <= result <= 1

def test_calc_efficiency_gap_single_district(single_district_map):
    # We will calculate these simpler metrics by hand and compare the function result

    # District One
    # 600 rep + 400 dem = 1000, 501 votes to win
    # Rep Wasted: 600 - 501 = 99, Dem Wasted: 400

    # Efficiecy Gap = (400 - 99) / 1000 * 1000 = 30.1

    result = calc_efficiency_gap(single_district_map)

    # Assertions
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == 30.1

def test_calc_efficiency_gap_multiple_districts(multiple_districts_map):
    # Just by looking at the sample district map, each party has equal wasted votes, so the efficiency gap should be 0.
    result = calc_efficiency_gap(multiple_districts_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == 0.0


def test_calc_efficiency_gap_dem_advantage(multiple_districts_map):
    # all districts sum to 1000, so 501 votes are needed to win

    # District One
    # 200 rep, 800 dem
    # Rep Wasted: 200, Dem Wasted: 800-501 = 299

    # District Two
    # 400 rep, 600 dem
    # Rep Wasted: 400, Dem Wasted: 600-501 = 99

    # District Three
    # 800 rep, 200 dem
    # Rep Wasted: 800 - 501 = 299, Dem Wasted: 200

    # District Four
    # 450 rep, 550 dem
    # Rep Wasted: 450, Dem Wasted: 550-501 = 49

    # Efficiecy Gap = ((200 + 400 + 299 + 450) - (299 + 99 + 200 + 49)/ 1000 * 1000 = -17.525
    multiple_districts_map['party_rep'] = [200, 400, 800, 450]
    multiple_districts_map['party_dem'] = [800, 600, 200, 550]
    result = calc_efficiency_gap(multiple_districts_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == -17.525

def test_calc_efficiency_gap_rep_advantage(multiple_districts_map):
    # all districts sum to 1000, so 501 votes are needed to win

    # District One
    # 800 rep, 200 dem
    # Rep Wasted: 800 - 501 = 299, Dem Wasted: 200

    # District Two
    # 600 rep, 400 dem
    # Rep Wasted: 600 - 501 = 99, Dem Wasted: 400

    # District Three
    # 200 rep, 800 dem
    # Rep Wasted: 200, Dem Wasted: 800 - 501 = 299

    # District Four
    # 550 rep, 450 dem
    # Rep Wasted: 550 - 501 = 49, Dem Wasted: 450

    # Efficiency Gap = ((299 + 99 + 200 + 49) - (200 + 400 + 299 + 450)) / 4000 * 100 = 17.525
    multiple_districts_map['party_rep'] = [800, 600, 200, 550]
    multiple_districts_map['party_dem'] = [200, 400, 800, 450]
    result = calc_efficiency_gap(multiple_districts_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == 17.525

def test_calc_mean_median_difference_single_district(single_district_map):
    # Single District
    # District One: 600 rep, 400 dem = 40.0% dem

    # Statewide Dem Percentage = 400 / (600 + 400) = 40.0%
    # Median Dem Percentage = 40.0% (only one district)
    # Mean-Median Difference = (40.0 - 40.0) * 100 = 0.0%

    result = calc_mean_median_difference(single_district_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == 0.0

def test_calc_mean_median_difference_base_multiple_districts(multiple_districts_map):
    # District Percentages and Calculation
    # District One: 600 rep, 400 dem = 40.0% dem
    # District Two: 400 rep, 600 dem = 60.0% dem
    # District Three: 300 rep, 700 dem = 70.0% dem
    # District Four: 700 rep, 300 dem = 30.0% dem

    # Statewide Dem Percentage = 2000 / 4000 = 50.0%
    # Median Dem Percentage = (40.0 + 60.0) / 2 = 50.0%
    # Mean-Median Difference = (50.0 - 50.0) * 100 = 0.0%

    result = calc_mean_median_difference(multiple_districts_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == 0.0

def test_calc_mean_median_difference_dem_advantage(multiple_districts_map):
    # District One: 200 rep, 800 dem = 80.0% dem
    # District Two: 400 rep, 600 dem = 60.0% dem
    # District Three: 800 rep, 200 dem = 20.0% dem
    # District Four: 450 rep, 550 dem = 55.0% dem

    # Statewide Dem Percentage:
    # Total Dem Votes = 800 + 600 + 200 + 550 = 2150
    # Total Votes = 1000 * 4 = 4000
    # Statewide Dem Percentage = 2150 / 4000 = 53.75%

    # Median of District Dem Percentages: (20.0, 55.0, 60.0, 80.0), Median = (55.0 + 60.0) / 2 = 57.5%
    # Mean-Median Difference = (53.75 - 57.5) * 100 = -3.75%

    multiple_districts_map['party_rep'] = [200, 400, 800, 450]
    multiple_districts_map['party_dem'] = [800, 600, 200, 550]
    result = calc_mean_median_difference(multiple_districts_map)
    assert isinstance(result, float), "Result should be a float."
    assert pytest.approx(result, 0.01) == -3.75, "Expected mean-median difference for Democrat advantage case is -3.75."


def test_calc_mean_median_difference_rep_advantage(multiple_districts_map):
    # District One: 800 rep, 200 dem = 20.0% dem
    # District Two: 600 rep, 400 dem = 40.0% dem
    # District Three: 200 rep, 800 dem = 80.0% dem
    # District Four: 550 rep, 450 dem = 45.0% dem

    # Total Dem Votes = 200 + 400 + 800 + 450 = 1850
    # Total Votes = 1000 * 4 = 4000
    # Statewide Dem Percentage = 1850 / 4000 = 46.25%

    # Median of District Dem Percentages: (20.0, 40.0, 45.0, 80.0), Median = (40.0 + 45.0) / 2 = 42.5%
    # Mean-Median Difference = (46.25 - 42.5) * 100 = 3.75%

    multiple_districts_map['party_rep'] = [800, 600, 200, 550]
    multiple_districts_map['party_dem'] = [200, 400, 800, 450]
    result = calc_mean_median_difference(multiple_districts_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == 3.75

def test_calc_lopsided_margins_democrat_advantage(multiple_districts_map):
    # District Percentages and Calculation
    # District One: 200 rep, 800 dem = 80.0% dem win
    # District Two: 400 rep, 600 dem = 60.0% dem win
    # District Three: 800 rep, 200 dem = 80.0% rep win
    # District Four: 450 rep, 550 dem = 55.0% dem win

    # Average Democrat Win Percent = (80.0 + 60.0 + 55.0) / 3 = 65.0%
    # Average Republican Win Percent = (80.0) / 1 = 80.0%
    # Lopsided Margin = 65.0 - 80.0 = -15.0%

    multiple_districts_map['party_rep'] = [200, 400, 800, 450]
    multiple_districts_map['party_dem'] = [800, 600, 200, 550]
    result = calc_lopsided_margins(multiple_districts_map)
    assert isinstance(result, float)
    assert pytest.approx(result, 0.01) == -15.0


def test_calc_lopsided_margins_republican_advantage(multiple_districts_map):
    # District Percentages and Calculation
    # District One: 800 rep, 200 dem = 80.0% rep win
    # District Two: 600 rep, 400 dem = 60.0% rep win
    # District Three: 200 rep, 800 dem = 80.0% dem win
    # District Four: 550 rep, 450 dem = 55.0% rep win

    # Average Democrat Win Percent = (80.0) / 1 = 80.0%
    # Average Republican Win Percent = (80.0 + 60.0 + 55.0) / 3 = 65.0%
    # Lopsided Margin = 80.0 - 65.0 = 15.0%

    multiple_districts_map['party_rep'] = [800, 600, 200, 550]
    multiple_districts_map['party_dem'] = [200, 400, 800, 450]
    result = calc_lopsided_margins(multiple_districts_map)
    assert isinstance(result, float), "Result should be a float."
    assert pytest.approx(result, 0.01) == 15.0, "Expected lopsided margin for Republican advantage is -18.33%."


def test_calc_lopsided_margins_no_advantage(single_district_map):
    # with one district, lopsided margins is not calculable
    result = calc_lopsided_margins(single_district_map)
    assert result is None

def test_calc_lopsided_margins_democrat_win_all(multiple_districts_map):
    # As Democrats win all the districts, the lopsided margin cannot be calculated
    multiple_districts_map['party_rep'] = [200, 400, 200, 450]
    multiple_districts_map['party_dem'] = [800, 600, 800, 550]
    result = calc_lopsided_margins(multiple_districts_map)
    assert result is None


def test_calc_lopsided_margins_republican_win_all(multiple_districts_map):
    # As Republicans win all the districts, the lopsided margin cannot be calculated
    multiple_districts_map['party_rep'] = [800, 600, 800, 550]
    multiple_districts_map['party_dem'] = [200, 400, 200, 450]
    result = calc_lopsided_margins(multiple_districts_map)
    assert result is None

def test_calc_dissimilarity_index_single_district(single_district_map):
    result = calc_dissimilarity_index(single_district_map)
    assert isinstance(result, dict)
    for key, value in result.items():
        assert pytest.approx(value, 0.01) == 0.0

def test_calc_dissimilarity_index_multiple_districts(multiple_districts_map):
    result = calc_dissimilarity_index(multiple_districts_map)

    assert isinstance(result, dict)

    for key, value in result.items():
        assert 0 <= value <= 1

    assert pytest.approx(result.get('eth1_hisp'), 0.01) == 0.200
    assert pytest.approx(result.get('eth1_aa'), 0.01) == 0.266
    assert pytest.approx(result.get('eth1_esa'), 0.01) == 0.140
    assert pytest.approx(result.get('eth2_81'), 0.01) == 0.176
    assert pytest.approx(result.get('eth1_oth'), 0.01) == 0.400

def test_calc_dissimilarity_index_missing_demographic(multiple_districts_map):
    multiple_districts_map.drop(columns=['eth1_esa'], inplace=True)
    result = calc_dissimilarity_index(multiple_districts_map)
    assert 'eth1_esa' not in result
    assert 'eth1_hisp' in result
    assert isinstance(result['eth1_hisp'], float)

def test_get_metric_dict(single_district_map, monkeypatch):
    mocked_dissimilarity_index = {
        'eth1_hisp': 0.8,
        'eth1_aa': 0.6,
        'eth1_esa': 0.7,
        'eth2_81': 0.5,
        'eth1_oth': 0.4
    }
    # We mock the results here, as this function is simply organizing the metric results
    # into a dictionary
    monkeypatch.setattr('fairymander.fairness.calc_avg_polsby_popper', lambda x: 0.5)
    monkeypatch.setattr('fairymander.fairness.calc_avg_reock', lambda x: 0.6)
    monkeypatch.setattr('fairymander.fairness.calc_efficiency_gap', lambda x: 0.1)
    monkeypatch.setattr('fairymander.fairness.calc_mean_median_difference', lambda x: 0.05)
    monkeypatch.setattr('fairymander.fairness.calc_lopsided_margins', lambda x: 0.03)
    monkeypatch.setattr('fairymander.fairness.calc_dissimilarity_index', lambda x: mocked_dissimilarity_index)

    result = get_metric_dict(single_district_map)

    assert isinstance(result, dict)
    assert result == {
        'Avg Polsby-Popper': 0.5,
        'Avg Reock': 0.6,
        'Efficiency Gap': 0.1,
        'Mean Median Difference': 0.05,
        'Lopsided Margin': 0.03,
        'Dissimilarity Indices': mocked_dissimilarity_index,
    }

def test_compare_maps_map_one_wins(map_a_metrics, map_b_metrics, monkeypatch):
    # Mocking get_metric_dict to return map_a and map_b
    monkeypatch.setattr('fairymander.fairness.get_metric_dict', lambda x: map_a_metrics if x == "map_one" else map_b_metrics)

    # Run the comparison
    map_one_wins, map_two_wins, ties = compare_maps("map_one", "map_two", verbose=False, show_maps=False)

    # Assertions
    assert 'Polsby-Popper' in map_one_wins
    assert 'Reock' in map_one_wins
    assert 'Efficiency Gap' in map_one_wins
    assert 'Mean Median Difference' in map_one_wins
    assert 'Dissimilarity Index: African American' in map_one_wins
    assert 'Dissimilarity Index: East and South Asian' in map_one_wins
    assert 'Dissimilarity Index: Hispanic' in map_one_wins
    assert 'Dissimilarity Index: Native American' in map_one_wins
    assert 'Lopsided Margin' in ties
    assert 'Dissimilarity Index: Other' in map_two_wins

def test_compare_maps_map_two_wins(map_a_metrics, map_b_metrics, monkeypatch):
    # Mocking get_metric_dict to return map_a and map_b
    monkeypatch.setattr('fairymander.fairness.get_metric_dict', lambda x: map_b_metrics if x == "map_one" else map_a_metrics)

    # Run the comparison
    map_one_wins, map_two_wins, ties = compare_maps("map_one", "map_two", verbose=False, show_maps=False)

    # Assertions
    assert 'Polsby-Popper' in map_two_wins
    assert 'Reock' in map_two_wins
    assert 'Efficiency Gap' in map_two_wins
    assert 'Mean Median Difference' in map_two_wins
    assert 'Dissimilarity Index: African American' in map_two_wins
    assert 'Dissimilarity Index: East and South Asian' in map_two_wins
    assert 'Dissimilarity Index: Hispanic' in map_two_wins
    assert 'Dissimilarity Index: Native American' in map_two_wins
    assert 'Lopsided Margin' in ties
    assert 'Dissimilarity Index: Other' in map_one_wins

def test_compare_maps_tie(map_a_metrics, map_b_metrics, monkeypatch):
    # Mocking get_metric_dict to return map_a and map_b
    monkeypatch.setattr('fairymander.fairness.get_metric_dict', lambda x: map_a_metrics)

    # Run the comparison
    map_one_wins, map_two_wins, ties = compare_maps("map_one", "map_two", verbose=False, show_maps=False)

    # Assertions
    assert not map_two_wins
    assert not map_two_wins
    assert 'Polsby-Popper' in ties
    assert 'Reock' in ties
    assert 'Efficiency Gap' in ties
    assert 'Mean Median Difference' in ties
    assert 'Lopsided Margin' in ties
    assert 'Dissimilarity Index: African American' in ties
    assert 'Dissimilarity Index: East and South Asian' in ties
    assert 'Dissimilarity Index: Hispanic' in ties
    assert 'Dissimilarity Index: Native American' in ties
    assert 'Dissimilarity Index: Other' in ties
