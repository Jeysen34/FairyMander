import pytest
from unittest.mock import patch, MagicMock
import os
import shutil
import geopandas as gpd
from shapely.geometry import Polygon
from fairymander.generator import DistrictGenerator
from fairymander.data import epsg

class TestDistrictGenerator:
    def test_district_generator_valid_inputs(self):
        generator = DistrictGenerator(prefix="az", deviation=0.05, steps=1000, num_maps=3, opt_metric_flag="compact")
        assert generator.prefix == "az"
        assert generator.deviation == 0.05
        assert generator.steps == 1000
        assert generator.num_maps == 3
        assert generator.opt_metric_flag == "compact"

        generator = DistrictGenerator(prefix="ny", deviation=0.03, steps=500, num_maps=5, opt_metric_flag="competitiveness")
        assert generator.prefix == "ny"
        assert generator.deviation == 0.03
        assert generator.steps == 500
        assert generator.num_maps == 5
        assert generator.opt_metric_flag == "competitiveness"

    @pytest.mark.parametrize("prefix", ["foo", "xy", "zz"])
    def test_invalid_prefix(self, prefix):
        with pytest.raises(ValueError, match=f"Invalid state prefix '{prefix}'"):
            DistrictGenerator(prefix=prefix, deviation=0.05, steps=1000, num_maps=3, opt_metric_flag="compact")

    @pytest.mark.parametrize("deviation", [0.11, 0.0009])
    def test_invalid_deviation(self, deviation):
        with pytest.raises(ValueError, match=f"Deviation '{deviation}' out of range. Must be between 0.001 and 0.1."):
            DistrictGenerator(prefix="az", deviation=deviation, steps=1000, num_maps=3, opt_metric_flag="compact")

    def test_invalid_steps(self):
        with pytest.raises(ValueError, match="Steps '-1' must be >= 0."):
            DistrictGenerator(prefix="az", deviation=0.05, steps=-1, num_maps=3, opt_metric_flag="compact")

    @pytest.mark.parametrize("num_maps", [0, 11])
    def test_invalid_num_maps(self, num_maps):
        with pytest.raises(ValueError, match=f"Number of maps '{num_maps}' out of range. Must be between 1 and 10."):
            DistrictGenerator(prefix="az", deviation=0.05, steps=1000, num_maps=num_maps, opt_metric_flag="compact")

    @pytest.mark.parametrize("opt_metric_flag", ["foo", "invalid_metric"])
    def test_invalid_opt_metric(self, opt_metric_flag):
        with pytest.raises(ValueError, match=f"Optimization metric '{opt_metric_flag}' is invalid. Must be 'compact' or 'competitiveness'"):
            DistrictGenerator(prefix="az", deviation=0.05, steps=1000, num_maps=3, opt_metric_flag=opt_metric_flag)

    def test_load_state_gdf(self):
        mocked_geo_df = MagicMock(spec=gpd.GeoDataFrame)
        mocked_geo_df.to_crs.return_value = None

        mocked_spec = MagicMock()
        mocked_spec.origin = "/fake/package/path"

        with patch("importlib.util.find_spec", return_value=mocked_spec):
            with patch("geopandas.read_file", return_value=mocked_geo_df) as mock_read_file:
                with patch("os.path.join", return_value="/fake/package/path/Data/finalData/az/az_bg_data.zip") as mock_path_join:
                    generator = DistrictGenerator(prefix="az", deviation=0.05, steps=1000, num_maps=3, opt_metric_flag="compact")

                    assert generator.state_gdf == mocked_geo_df
                    mocked_geo_df.to_crs.assert_called_once_with(epsg=epsg['az'], inplace=True)
                    mock_path_join.assert_called_with("/fake/package", "Data/finalData/az/az_bg_data.zip")

    def create_mock_geodataframe(self):
        data = {
            "geometry": [Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])],
            "attribute": ["test_value"]
        }
        return gpd.GeoDataFrame(data, crs="EPSG:4326")

    @patch.object(DistrictGenerator, 'run', return_value=[create_mock_geodataframe(None), create_mock_geodataframe(None)])
    def test_run_and_save_dir_doesnt_exist(self, mock_run):
        generator = DistrictGenerator("az", 0.05, 10, 3, "compact")
        test_directory = "test_map_dir"
        new_prefix = "new_prefix"

        generator.run_and_save(test_directory, new_prefix)

        assert os.path.exists(f"{test_directory}/{new_prefix}")

        for index in range(len(mock_run.return_value)):
            shapefile_path = f"{test_directory}/{new_prefix}/{new_prefix}-{index}/{new_prefix}-{index}.shp"
            assert os.path.exists(shapefile_path)
            loaded_gdf = gpd.read_file(shapefile_path)
            assert not loaded_gdf.empty

        shutil.rmtree(f"{test_directory}")

    @patch.object(DistrictGenerator, 'run', return_value=[create_mock_geodataframe(None), create_mock_geodataframe(None)])
    def test_run_and_save_dir_exists(self, mock_run):
        generator = DistrictGenerator("az", 0.05, 10, 3, "compact")
        test_directory = "test_map_dir"
        new_prefix = "existing_prefix"

        existing_path = f"{test_directory}/{new_prefix}/{new_prefix}-0"
        os.makedirs(existing_path)

        generator.run_and_save(test_directory, new_prefix)

        assert os.path.exists(f"{test_directory}/{new_prefix}")

        for index in range(len(mock_run.return_value)):
            shapefile_path = f"{test_directory}/{new_prefix}/{new_prefix}-{index}/{new_prefix}-{index}.shp"
            assert os.path.exists(shapefile_path)
            loaded_gdf = gpd.read_file(shapefile_path)
            assert not loaded_gdf.empty

        shutil.rmtree(test_directory)
