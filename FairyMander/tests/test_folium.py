import pytest
import geopandas as gpd
import folium
from unittest.mock import patch, MagicMock, ANY
from fairymander.data import get_curr_district_file
from pyogrio.errors import DataSourceError
from fairymander.folium_converter import map_to_folium, map_to_folium_from_file

curr_az = get_curr_district_file("az")
curr_ma = get_curr_district_file("ma")
generated_az = gpd.read_file(f"zip://example_generated_map/az_Efficiency-Gap_districts1.zip")


@pytest.mark.parametrize("state, district_gdf", [("ma", curr_ma), ("az", curr_az), ("az", generated_az)])
def test_map_to_folium_valid_state(state, district_gdf):
    result = map_to_folium(state, district_gdf)

    assert isinstance(result, folium.Map)

    assert len(result._children) > 0

def test_map_to_foilum_invalid_state():
    with pytest.raises(KeyError):
        map_to_folium("foo", curr_az)

@patch("fairymander.folium_converter.map_to_folium")
def test_map_to_folium_from_file_file_found(mock_map_to_folium):
    mock_map_to_folium.return_value = MagicMock()
    result = map_to_folium_from_file("az", "zip://example_generated_map/az_Efficiency-Gap_districts1.zip")
    mock_map_to_folium.assert_called_once_with("az", ANY)
    assert result == mock_map_to_folium.return_value

def test_map_to_folium_from_file_file_not_found():
    with pytest.raises(DataSourceError):
        map_to_folium_from_file("az", "foo")
