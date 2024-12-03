import pytest
import geopandas as gpd
from fairymander.data import get_curr_district_file


@pytest.mark.parametrize("prefix", ["az", "nh"]) # nh is to check for 'ZZ''
def test_get_curr_district_file_exists(prefix):
    result = get_curr_district_file(prefix)

    assert isinstance(result, gpd.GeoDataFrame)

    expected_columns = [
        "District",
        "C_TOT22",
        "party_dem",
        "party_rep",
        "party_oth",
        "eth1_eur",
        "eth1_hisp",
        "eth1_aa",
        "eth1_esa",
        "eth2_81",
        "geometry",
    ]
    for column in expected_columns:
        assert column in result.columns

    assert not result.empty

def test_get_curr_district_file_invalid_prefix():
    with pytest.raises(KeyError):
        get_curr_district_file("foo")
