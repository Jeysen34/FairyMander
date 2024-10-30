import geopandas as gpd
import importlib.util
import os


"""
Module for obtaining data relevant to FairyMander district generation and comparison
"""
package_path = os.path.dirname(importlib.util.find_spec("fairymander.data").origin)

# dict for the number of districts each state is apportioned
num_districts = {
    'al': 7, 'az': 9, 'ar': 4,
    'ca': 52, 'co': 8, 'ct': 5,
    'de': 1, 'fl': 28, 'ga': 14,
    'id': 2, 'il': 17, 'in': 9,
    'ia': 4, 'ks': 4, 'la': 6,
    'me': 2, 'md': 8, 'ma': 9,
    'mi': 13, 'mn': 8, 'ms': 4,
    'mo': 8, 'mt': 2, 'ne': 3,
    'nv': 4, 'nh': 2, 'nj': 12,
    'nm': 3, 'ny': 26, 'nc': 14,
    'nd': 1, 'oh': 15, 'ok': 5,
    'or': 6, 'pa': 17, 'sc': 7,
    'sd': 1, 'tn': 9, 'tx': 38,
    'ut': 4, 'vt': 1, 'va': 11,
    'wa': 10, 'wv': 2, 'wi': 8,
    'wy': 1
}

# dict determining the epsg code we will use for geographic projection
epsg = {
    'al': 26930, 'az': 26949, 'ar': 26952,
    'ca': 3310, 'co': 26954, 'ct': 26956,
    'de': 26957, 'fl': 3086, 'ga': 26966,
    'id': 26969, 'il': 103270, 'in': 26973,
    'ia': 7551, 'ks': 6922, 'la': 32199,
    'me': 26983, 'md': 26985, 'ma': 26987,
    'mi': 26989, 'mn': 26992, 'ms': 3814,
    'mo': 26997, 'mt': 32100, 'ne': 32104,
    'nv': 32108, 'nh': 32110, 'nj': 32111,
    'nm': 32114, 'ny': 32118, 'nc': 32119,
    'nd': 32120, 'oh': 32123, 'ok': 32124,
    'or': 8328, 'pa': 32128, 'sc': 32033,
    'sd': 32135, 'tn': 32136, 'tx': 32139,
    'ut': 32043, 'vt': 32145, 'va': 3968,
    'wa': 7582, 'wv': 32150, 'wi': 32153,
    'wy': 32159
}

# dict with each state id number, padded with zeros for single digits
id_map = {
    'al': '01', 'az': '04', 'ar': '05',
    'ca': '06', 'co': '08', 'ct': '09',
    'de': '10', 'fl': '12', 'ga': '13',
    'id': '16', 'il': '17', 'in': '18',
    'ia': '19', 'ks': '20', 'la': '22',
    'me': '23', 'md': '24', 'ma': '25',
    'mi': '26', 'mn': '27', 'ms': '28',
    'mo': '29', 'mt': '30', 'ne': '31',
    'nv': '31', 'nh': '33', 'nj': '34',
    'nm': '35', 'ny': '36', 'nc': '37',
    'nd': '38', 'oh': '39', 'ok': '40',
    'or': '41', 'pa': '42', 'sc': '45',
    'sd': '46', 'tn': '47', 'tx': '48',
    'ut': '49', 'vt': '50', 'va': '51',
    'wa': '53', 'wv': '54', 'wi': '55',
    'wy': '56'
}

# dict with initial lattitude, longitude, and zoom for displaying state maps in folium
file_path = os.path.join(package_path, 'FoliumLongLat.csv')
df = gpd.read_file(file_path)
folium_longlat = {
    row['state'].split('_', 1)[1]: tuple(row[['latitude', 'longitude', 'zoom_start']])
    for _, row in df.iterrows()
}


def get_curr_district_file(prefix: str) -> gpd.GeoDataFrame:
    """
    Gets the current district file for fairness evalaution by joining and cleaning the
    current shapefile with the voter data from Dave's

    Parameters
    ----------
    prefix: str
        the two letter abbreviation for the state the district map belongs to (i,e, az, fl, ny)

    Returns
    -------
    res_gdf: GeoDataFrame
        a geopandas dataframe containing the voting and shape data for the current district plan
    """
    geo_file_path = os.path.join(package_path, f"../Data/CurrentCongressionalDistricts/st{id_map[prefix]}_{prefix}/tl_2023_{id_map[prefix]}_cd118.shp")
    voter_file_path = os.path.join(package_path, f"../Data/CurrentCongressionalDistricts/st{id_map[prefix]}_{prefix}/{prefix}-district-statistics.csv")
    geo_df = gpd.read_file(geo_file_path)
    voter_csv = gpd.read_file(voter_file_path)
    voter_csv = voter_csv.drop([voter_csv.index[0], voter_csv.index[-1]])

    geo_df['CD118FP'] = geo_df['CD118FP'].astype(int)
    voter_csv['ID'] = voter_csv['ID'].astype(int)

    geo_df = geo_df.rename(columns={'CD118FP': 'ID'})
    geo_df = geo_df[['ID', 'geometry']]
    res = voter_csv.merge(geo_df, on='ID')

    convert_to_total = ['Dem', 'Rep', 'Oth', 'White', 'Minority', 'Hispanic', 'Black', 'Asian', 'Native', 'Pacific']

    for column in convert_to_total:
        res[column] = res[column].astype(float) * res['Total VAP'].astype(int)
        res[column] = res[column].astype(int)

    res['total_reg'] = res['Dem'] + res['Rep'] + res['Oth']
    res['eth1_oth'] = res['Native'] + res['Pacific']

    res = res.rename(columns={'ID': 'District',
                            'Total Pop': 'C_TOT22',
                            'Dem': 'party_dem',
                            'Rep': 'party_rep',
                            'Oth': 'party_oth',
                            'White': 'eth1_eur',
                            'Hispanic': 'eth1_hisp',
                            'Black': 'eth1_aa',
                            'Asian': 'eth1_esa',
                            'Native': 'eth2_81'})
    res_gdf = gpd.GeoDataFrame(res, geometry='geometry')
    res_gdf.to_crs(epsg=epsg[prefix], inplace=True)

    return res_gdf