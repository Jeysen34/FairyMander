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


epsg = {
    'al': 26930, 'az': 26949, 'ar': 26952,
    'ca': 3310, 'co': 26954, 'ct': 26956,
    'de': 26957, 'fl': 3086, 'ga': 4722,
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
    res['eth1_oth'] = res['Native'] + res['Pacific']

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
    res_gdf.to_crs(epsg=epsg[prefix], inplace=True)

    return res_gdf

#print(get_curr_district_file('az').head())
#print(get_curr_district_file('az').columns)