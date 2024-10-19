import geopandas as gpd

"""
This module is used to "clean" current district shapefiles by combining the existing
shapefile with voting data from Dave's Redistricting Data. It will reassign the fields
in the shapefile so the file is compatible to compare with FairyMander's generated districts
"""

# TODO: add all Dave's redistricting files in the 'Data' folder

# TODO: abstract id_map in the FairyMander package so we can just import it from a module, like 'import state_id_map from fairymander.data'
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

def get_curr_district_file(prefix):
    """
    The main function for this module. Gets the current district file for fairness evalaution by
    joining and cleaning the current shapefile with the voter data from Dave's
    """
    geo_df = gpd.read_file(f"../Data/CurrentCongressionalDistricts/st{id_map[prefix]}_{prefix}/tl_2023_{id_map[prefix]}_cd118.shp")
    voter_csv = gpd.read_file(f"../Data/CurrentCongressionalDistricts/st{id_map[prefix]}_{prefix}/{prefix}-district-statistics.csv")
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

    res = res.rename(columns={'ID': 'District',
                            'Total Pop': 'C_TOT22',
                            'Dem': 'party_dem',
                            'Rep': 'party_rep',
                            'Oth': 'party_oth',
                            'White': 'eth1_eur',
                            'Hispanic': 'eth1_hisp',
                            'Black': 'eth1_aa',
                            'Asian': 'eth1_esa'})
    res_gdf = gpd.GeoDataFrame(res, geometry='geometry')

    return res_gdf

print(get_curr_district_file('az').head())