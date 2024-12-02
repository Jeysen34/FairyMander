
import pytest
import geopandas as gpd
from gerrychain import GeographicPartition
from gerrychain.partition.assignment import Assignment
from fairymander.generator import DistrictGenerator

@pytest.mark.parametrize(
    "prefix, deviation, steps, num_maps, opt_metric_flag",
    [
        ("az", 0.05, 1000, 3, "compact"),
        ("az", 0.05, 1000, 3, "competitiveness"),
        ("az", 0.008, 1000, 3, "compact"),
        ("ma", 0.05, 1000, 3, "compact"),
    ]
)
def test_get_random_partition(prefix, deviation, steps, num_maps, opt_metric_flag):
    district_gen = DistrictGenerator(prefix, deviation, steps, num_maps, opt_metric_flag)

    partition = district_gen._get_random_partition()

    assert isinstance(partition, GeographicPartition)
    assert "population" in partition.updaters
    assert "cut_edges" in partition.updaters

    if opt_metric_flag == "compact":
        assert "polsby-popper" in partition.updaters
    else:
        assert "election" in partition.updaters

    populations = partition["population"]
    total_population = sum(populations.values())
    ideal_population = total_population / len(partition.parts)
    max_population = (1 + deviation) * ideal_population
    min_population = (1 - deviation) * ideal_population

    for district, pop in populations.items():
        assert min_population <= pop <= max_population

@pytest.fixture
def district_generator_compact():
    return DistrictGenerator(
        prefix="az",
        deviation=0.05,
        steps=100,
        num_maps=2,
        opt_metric_flag="compact"
    )

@pytest.fixture
def district_generator_competitive():
    return DistrictGenerator(
        prefix="az",
        deviation=0.05,
        steps=100,
        num_maps=2,
        opt_metric_flag="competitiveness"
    )

def test_generate_maps_compact(district_generator_compact):
    test_partition = district_generator_compact._get_random_partition()

    result = district_generator_compact._generate_maps(test_partition)

    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert isinstance(item[0], float)
        print(type(item[1]))

        assert isinstance(item[1], Assignment)

    best = district_generator_compact.best
    assert len(best) <= district_generator_compact.num_maps

    best_scores = [item[0] for item in best]
    assert len(best_scores) == len(set(best_scores))
    assert all(score in district_generator_compact.seen_scores for score in best_scores)

    expected_best_scores = sorted(district_generator_compact.seen_scores, reverse=True)[:district_generator_compact.num_maps]
    assert sorted(best_scores) == sorted(expected_best_scores)

    for i in range(1, len(best)):
        assert best[i][0] >= best[i - 1][0]

def test_generate_maps_competitive(district_generator_competitive):
    test_partition = district_generator_competitive._get_random_partition()

    result = district_generator_competitive._generate_maps(test_partition)

    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert isinstance(item[0], float)
        print(type(item[1]))
        assert isinstance(item[1], Assignment)

    best = district_generator_competitive.best
    assert len(best) <= district_generator_competitive.num_maps

    best_scores = [item[0] for item in best]
    assert len(best_scores) == len(set(best_scores))
    assert all(score in district_generator_competitive.seen_scores for score in best_scores)

    expected_best_scores = sorted(district_generator_competitive.seen_scores, reverse=True)[:district_generator_competitive.num_maps]
    assert sorted(best_scores) == sorted(expected_best_scores)
    for i in range(1, len(best)):
        assert best[i][0] >= best[i - 1][0]

def test_run_compact(district_generator_compact, mocker):
    mocker.patch("matplotlib.pyplot.show")
    mocker.patch("builtins.print")

    result = district_generator_compact.run()

    assert isinstance(result, list)
    assert len(result) == district_generator_compact.num_maps

    for gdf in result:
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert 'District' in gdf.columns
        assert gdf['District'].nunique() > 1

        for district_id in gdf['District'].unique():
            district_rows = gdf[gdf['District'] == district_id]
            assert len(district_rows) == 1
        assert all(gdf['District'] == range(1, len(gdf) + 1))

def test_run_competitive(district_generator_competitive, mocker):
    mocker.patch("matplotlib.pyplot.show")
    mocker.patch("builtins.print")

    result = district_generator_competitive.run()

    assert isinstance(result, list)
    assert len(result) == district_generator_competitive.num_maps

    for gdf in result:
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert 'District' in gdf.columns
        assert gdf['District'].nunique() > 1

        for district_id in gdf['District'].unique():
            district_rows = gdf[gdf['District'] == district_id]
            assert len(district_rows) == 1
        assert all(gdf['District'] == range(1, len(gdf) + 1))
