# Import the libraries
import geopandas as gpd
import numpy as np
from math import floor
from statistics import median
import matplotlib.pyplot as plt

"""
Group of functions for performing district fairness calculations.
Make sure you have dissolved the map before using this module.
"""

eth_common_names = {
    'eth1_aa': 'African American',
    'eth1_esa': 'East and South Asian',
    'eth1_hisp': 'Hispanic',
    'eth2_81': 'Native American',
    'eth1_oth': 'Other'
}

def get_metric_dict(test_map: gpd.GeoDataFrame) -> dict:
    """
    Returns a dictionary containing all of the fairness metrics for the given GeoDataFrame map.

    Parameters
    ----------
    test_map : GeoDataFrame
        GeoPandas DataFrame containing the district map to be evaluated for fairness.

    Returns
    -------
    result_dict : dict
        Dictionary containing all of the fairness metrics for the given district plan.
    """
    result_dict = {
            'Avg Polsby-Popper': calc_avg_polsby_popper(test_map),
            'Avg Reock': calc_avg_reock(test_map),
            'Efficiency Gap': calc_efficiency_gap(test_map),
            'Mean Median Difference': calc_mean_median_difference(test_map),
            'Lopsided Margin': calc_lopsided_margins(test_map),
            'Dissimilarity Indices': calc_dissimilarity_index(test_map)
    }

    return result_dict

def full_analysis(test_map: gpd.GeoDataFrame, verbose: bool = False, show_map: bool = True) -> None:
    """
    Performs a series of outputs detailing the fairness metrics for the given district map.

    Parameters
    ----------
    test_map : GeoDataFrame
        GeoPandas DataFrame containing the district map to be evaluated for fairness.

    verbose : bool
        Indicates a verbose output, which will provide descriptions of the metrics along
        with their values.

    show_map : bool
        Indicates whether the analysis should show the map itself, plotted as a geography.
    """
    if show_map:
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        test_map.plot(column='District', ax=ax, legend=True, cmap="rainbow")
        plt.title("District Map")
        plt.show()
    print("Running Fairness Analysis")
    print("-------------------------")
    if verbose:
        print("The Polsby-Popper Score is a district compactness measure. It is the ratio between a district's area and its perimeter.")
        print("Ranges from 0-1, with values closer to 1 meaning higher compactness.")
    print(f"Average Polsby-Popper Score: {calc_avg_polsby_popper(test_map)}")
    print()
    if verbose:
        print("The Reock Score is a district compactness measure. It is the ratio between a district's area and the area of a minimum bounding circle around the district.")
        print("Ranges from 0-1, with values closer to 1 meaning higher compactness.")
    print(f"Average Reock Score: {calc_avg_reock(test_map)}")
    print()
    if verbose:
        print("The Efficiency Gap is a district competitiveness measure. It uses wasted votes in an election (i.e., votes that didn't contribute to the election outcome) to quantify partisanship.")
        print("A percent difference 0-100, where a negative (-) value indicates a Democrat advantage, while a positive (+) value indicates a Republican advantage.")
    print(f"Efficiency Gap: {calc_efficiency_gap(test_map)}")
    print()
    if verbose:
        print("The Mean Median Difference is a district competitiveness measure. It is the difference between a party's average vote share and its median vote share across all districts.")
        print("A percent difference 0-100, where a negative (-) value indicates a Democrat advantage, while a positive (+) value indicates a Republican advantage.")
    print(f"Mean Median Difference: {calc_mean_median_difference(test_map)}")
    print()
    if verbose:
        print("The Lopsided Margin test is a district competitiveness measure. It is the difference between the average percentages by which each party won in a district.")
        print("A percent difference 0-100, where a negative (-) value indicates Republicans have been packed (i.e., a Democrat advantage), while a positive (+) value indicates Democrats have been packed (i.e., a Republican advantage).")
    lopsided_margin = calc_lopsided_margins(test_map)
    if lopsided_margin:
        print(f"Lopsided Margin Score: {calc_lopsided_margins(test_map)}")
    else:
        print("One party won every district, so lopsided margin is not calculable.")
    print()
    if verbose:
        print("The Dissimilarity Index is a district minority representation measure. Each index indicates how spread out the minority population is across the district plan.")
        print("Ranges from 0-1, with values closer to 1 indicating higher minority segregation between districts.")
    diss_index_res = calc_dissimilarity_index(test_map)
    for ethnicity, diss_index in diss_index_res.items():
        print(f"Dissimilarity index, {eth_common_names[ethnicity]}: {diss_index}")
    print()

def calc_avg_reock(test_map: gpd.GeoDataFrame) -> float:
    """
    The Reock score measures whether the district is compact or not.
    The score ranges from 0-1, with values closer to 1 indicating compactness.
    Calculates the average Reock score for the given test map.

    Parameters
    ----------
    test_map : GeoDataFrame
        GeoPandas DataFrame containing the district map to be evaluated for the Reock score.

    Returns
    -------
    float :
        Average Reock score for the districts in the map, ranging from 0-1.
    """

    # Get the number of districts, in this case the number of rows in the map
    num_districts = test_map.shape[0]

    # Get the minimum bounding circles
    min_bounding_circles = test_map.minimum_bounding_circle()

    # Initialize average Reock score
    average_reock_score = 0

    # Get the average Reock score for each district
    for district_num in range(0, num_districts):
        district_area = test_map.loc[district_num, 'geometry'].area
        min_bounding_circle_area = min_bounding_circles[district_num].area
        average_reock_score += district_area / min_bounding_circle_area

    # Return average
    return average_reock_score / num_districts

def calc_avg_polsby_popper(test_map: gpd.GeoDataFrame) -> float:
    """
    The Polsby-Popper score calculates the compactness of the district. It is the ratio between the perimeter
    and the area of the district.
    The score ranges from 0-1, with values closer to 1 indicating compactness.
    Calculates the average Polsby-Popper score for the given test map.

    Parameters
    ----------
    test_map : GeoDataFrame
        GeoPandas DataFrame containing the district map to be evaluated for the Polsby-Popper score.

    Returns
    -------
    float :
        Average Polsby-Popper score for the districts in the map, ranging from 0-1.
    """

    # Get the number of districts, in this case the number of rows in the map
    num_districts = test_map.shape[0]

    # Initialize average Polsby-Popper score
    avg_pp_score = 0

    # Calculate Polsby-Popper for districts in the map
    for district_num in range(num_districts):
        district_area = test_map.loc[district_num, 'geometry'].area
        district_perimeter = test_map.loc[district_num, 'geometry'].length
        avg_pp_score += (4 * np.pi) * (district_area / (district_perimeter ** 2))

    # Return average
    return avg_pp_score / num_districts

def calc_efficiency_gap(test_map: gpd.GeoDataFrame) -> float:
    """
    The Efficiency Gap measures political competitiveness. It is a percentage ranging from 0-100.
    If the Efficiency Gap is positive (+), it means that Party A (in this case, Republican) has an advantage.
    If the Efficiency Gap is negative (-), it means that Party B (in this case, Democrat) has an advantage.

    Parameters
    ----------
    test_map : GeoDataFrame
        GeoPandas DataFrame containing the district map to be evaluated for the efficiency gap.

    Returns
    -------
    float :
        Efficiency gap for the district map, ranging from 0-100.
        (-) value indicates Democrat Advantage.
        (+) value indicates Republican Advantage.
    """
    wasted_votes_rep = 0
    wasted_votes_dem = 0
    total_votes = 0

    # Calculate efficiency gap for district map, formula = (Wasted Dem Votes - Wasted Rep Votes) / total votes
    for _, district in test_map.iterrows():
        district_votes = district['party_rep'] + district['party_dem']
        total_votes += district_votes
        votes_to_win = floor(district_votes / 2) + 1
        if district['party_rep'] > district['party_dem']:
            wasted_votes_dem += district['party_dem']
            wasted_votes_rep += district['party_rep'] - votes_to_win
        else:
            wasted_votes_rep += district['party_rep']
            wasted_votes_dem += district['party_dem'] - votes_to_win

    return ((wasted_votes_dem - wasted_votes_rep) / total_votes) * 100

def calc_mean_median_difference(test_map: gpd.GeoDataFrame) -> float:
    """
    Mean Median Difference is a district competitiveness measure. It is the difference
    between a party's average vote share and its median vote share across all districts. It is a percentage ranging from 0-100.
    A negative (-) value indicates a Democrat advantage.
    A positive (+) value indicates a Republican advantage.

    Parameters
    ----------
    test_map : GeoDataFrame
        GeoPandas DataFrame containing the district map to be evaluated for the mean median difference.

    Returns
    -------
    float :
        Mean median difference for the district map, ranging from 0-100.
        (-) value indicates Democrat Advantage.
        (+) value indicates Republican Advantage.
    """
    dem_percentages = []
    total_votes = 0

    for _, district in test_map.iterrows():
        district_votes = district['party_rep'] + district['party_dem']
        total_votes += district_votes
        dem_percentages.append(district['party_dem'] / district_votes)

    dem_percentage_statewide = test_map['party_dem'].sum() / total_votes

    return 100 * (dem_percentage_statewide - median(dem_percentages))

def calc_lopsided_margins(test_map: gpd.GeoDataFrame) -> float | None:
    """
    The Lopsided Margin test is a district competitiveness measure. It is the difference
    between the average percentages by which each party won in a district. It is a percentage ranging from 0-100.
    A negative (-) value indicates Republicans have been packed (i.e., a Democrat advantage).
    A positive (+) value indicates Democrats have been packed (i.e., a Republican advantage).

    Parameters
    ----------
    test_map: GeoDataFrame
        GeoPandas DataFrame containing the district map to be evaluated for the lopsided margin test.

    Returns
    -------
    float :
        Lopsided margin test for the district map, ranging from 0-100.
        (-) value indicates Democrat Advantage.
        (+) value indicates Republican Advantage.
        None if lopsided margin cannot be calculated, i.e., if one party won every district.
    """
    dem_win_percents = []
    rep_win_percents = []
    for _, district in test_map.iterrows():
        district_votes = district['party_rep'] + district['party_dem']
        if district['party_rep'] > district['party_dem']:
            rep_win_percents.append((district['party_rep'] / district_votes) * 100)
        else:
            dem_win_percents.append((district['party_dem'] / district_votes) * 100)

    # If one party won every district, then it's impossible to calculate lopsided margin
    if len(dem_win_percents) == 0:
        print("Republicans won every district, so lopsided margin cannot be calculated.")
        return None
    if len(rep_win_percents) == 0:
        print("Democrats won every district, so lopsided margin cannot be calculated.")
        return None

    return (sum(dem_win_percents) / len(dem_win_percents)) - (sum(rep_win_percents) / len(rep_win_percents))

def calc_dissimilarity_index(test_map: gpd.GeoDataFrame) -> dict:
    """
    The Dissimilarity Index is a district minority representation measure. Each index indicates
    how spread out the minority population is across the district plan. Indices range from 0-1,
    with values closer to 1 indicating higher minority segregation between districts.

    Parameters
    ----------
    test_map: GeoDataFrame
        GeoPandas DataFrame containing the district map to be evaluated for dissimilarity indices.

    Returns
    -------
    dict :
        In the form [minority group]: dissimilarity index, with indices closer to 1 indicating
        more segregation.
    """
    # Make a list of demographic headers
    demographics = ['eth1_hisp', 'eth1_aa','eth1_esa', 'eth2_81', 'eth1_oth']
    tot_white_pop = test_map['eth1_eur'].sum()
    num_districts = test_map.shape[0]
    dis_indices = {}

    for demographic in demographics:
        if demographic in test_map.columns:

            tot_minority_pop = test_map[demographic].sum()
            dis_index = 0

            for district_num in range(num_districts):
                district_white_pop = test_map.loc[district_num, 'eth1_eur']
                district_minority_pop = test_map.loc[district_num, demographic]
                dis_index += abs((district_minority_pop / tot_minority_pop) - (district_white_pop / tot_white_pop))

            dis_index *= 1/2

            dis_indices[demographic] = dis_index
        else:
            print(f"{demographic} not found in map.")
    return dis_indices

def compare_maps(map_one, map_two, verbose=False, show_maps = True):
    """
    Performs a comparison operation between the two given maps' fairness metrics, showing a final
    comparison between them

    Parameters
    ----------
    map_one : GeoDataFrame
        geopandas dataframe containing the first district map to be compared

    map_two : GeoDataFrame
        geopandas dataframe containing the second district map to be compared

    verbose : bool
        indicates a verbose output, which will provide descriptions of the metrics along
        with their values

    show_maps : bool
        indicates whether the analysis should show the maps, plotted as geographies
    """
    if show_maps:
        fig, ax = plt.subplots(1, 2, figsize=(20, 10))

        # Plot the first map
        map_one.plot(column='District', ax=ax[0], legend=True, cmap="rainbow")
        ax[0].set_title("District Map One")

        # Plot the second map
        map_two.plot(column='District', ax=ax[1], legend=True, cmap="rainbow")
        ax[1].set_title("District Map Two")

        plt.tight_layout()
        plt.show()
    map_one_winning_metrics = []
    map_two_winning_metrics = []
    ties = []

    map_one_metrics = get_metric_dict(map_one)
    map_two_metrics = get_metric_dict(map_two)

    print("Running Fairness Comparison Analysis")
    print("------------------------------------")
    if verbose:
        print("The Polsby-Popper Score is a district compactness measure. It is the ratio between a district's area and its perimeter.")
        print("Ranges from 0-1, with values closer to 1 meaning higher comapctness")
    print(f"Average Polsby-Popper Score for Map 1: {map_one_metrics['Avg Polsby-Popper']}")
    print(f"Average Polsby-Popper Score for Map 2: {map_two_metrics['Avg Polsby-Popper']}")
    if map_one_metrics['Avg Polsby-Popper'] > map_two_metrics['Avg Polsby-Popper']:
        print("Map One has a better Polsby-Popper score")
        map_one_winning_metrics.append('Polsby-Popper')
    elif map_one_metrics['Avg Polsby-Popper'] < map_two_metrics['Avg Polsby-Popper']:
        print("Map Two has a better Polsby-Popper score")
        map_two_winning_metrics.append('Polsby-Popper')
    else:
        print("Both maps have the same Polsby-Popper score")
        ties.append("Polsby-Popper")
    print()
    if verbose:
        print("The Reock Score is a district compactness measure. It is the ratio between a district's area and the area of a minimum bounding circle around the district.")
        print("Ranges from 0-1, with values closer to 1 meaning higher comapctness")
    print(f"Average Reock Score for Map 1: {map_one_metrics['Avg Reock']}")
    print(f"Average Reock Score for Map 2: {map_two_metrics['Avg Reock']}")
    if map_one_metrics['Avg Reock'] > map_two_metrics['Avg Reock']:
        print("Map One has a better Reock score")
        map_one_winning_metrics.append('Reock')
    elif map_one_metrics['Avg Reock'] < map_two_metrics['Avg Reock']:
        print("Map Two has a better Reock score")
        map_two_winning_metrics.append('Reock')
    else:
        print("Both maps have the same Reock score")
        ties.append("Reock")
    print()
    if verbose:
        print("The Efficiency Gap is a district competitiveness measure. It uses wasted votes in an election (i.e., votes that didn't contribute to the election outcome) to quantify partisanship")
        print("A percent difference 0-100, where a negative (-) value indicates a Democrat advantage, while a positive (+) value indicates a Republican advantage")
    print(f"Efficiency Gap for Map 1: {map_one_metrics['Efficiency Gap']}")
    print(f"Efficiency Gap for Map 2: {map_two_metrics['Efficiency Gap']}")
    if abs(map_one_metrics['Efficiency Gap']) < abs(map_two_metrics['Efficiency Gap']):
        print("Map One has a better Efficiency Gap")
        map_one_winning_metrics.append('Efficiency Gap')
    elif abs(map_one_metrics['Efficiency Gap']) > abs(map_two_metrics['Efficiency Gap']):
        print("Map Two has a better Efficiency Gap")
        map_two_winning_metrics.append('Efficiency Gap')
    else:
        print("Both maps have the same Efficiency Gap")
        ties.append('Efficiency Gap')
    print()
    if verbose:
        print("The Mean Median Difference is a district competitiveness measure. It is the difference between a party's average vote share and its median vote share across all districts")
        print("A percent difference 0-100, where a negative (-) value indicates a Democrat advantage, while a positive (+) value indicates a Republican advantage")
    print(f"Mean Median Difference, Map One: {map_one_metrics['Mean Median Difference']}")
    print(f"Mean Median Difference, Map Two: {map_two_metrics['Mean Median Difference']}")
    if abs(map_one_metrics['Mean Median Difference']) < abs(map_two_metrics['Mean Median Difference']):
        print("Map One has a better Mean Median Difference")
        map_one_winning_metrics.append('Mean Median Difference')
    elif abs(map_one_metrics['Mean Median Difference']) > abs(map_two_metrics['Mean Median Difference']):
        print("Map Two has a better Mean Median Difference")
        map_two_winning_metrics.append('Mean Median Difference')
    else:
        print("Both maps have the same Mean Median Difference")
        ties.append("Mean Median Difference")
    print()
    if verbose:
        print("The Lopsided Margin test is a district competitiveness measure. It is the difference between the average percentages by which each party won in a district.")
        print("A percent difference 0-100, where a negative (-) value indicates Republicans have been packed (i.e., a Democrat advantage), where a positive (+) value indicates Democrats have been packed (i.e., a Republican advantage")
    if map_one_metrics['Lopsided Margin']:
        print(f"Lopsided Margin Score, Map One: {map_one_metrics['Lopsided Margin']}")
    else:
        print("One party won every district in Map One, so lopsided margin is not calculable.")
    if map_two_metrics['Lopsided Margin']:
        print(f"Lopsided Margin Score, Map Two: {map_two_metrics['Lopsided Margin']}")
    else:
        print("One party won every district in Map Two, so lopsided margin is not calculable.")
    if map_one_metrics['Lopsided Margin'] and map_two_metrics['Lopsided Margin']:
        if abs(map_one_metrics['Lopsided Margin']) < abs(map_two_metrics['Lopsided Margin']):
            print("Map One has a better Lopsided Margin Score")
            map_one_winning_metrics.append('Lopsided Margin')
        elif abs(map_one_metrics['Lopsided Margin']) > abs(map_two_metrics['Lopsided Margin']):
            print("Map Two has a better Lopsided Margin Score")
            map_two_winning_metrics.append('Lopsided Margin')
        else:
            ties.append('Lopsided Margin')
            print("Both maps have the same Lopsided Margin Score")
    print()
    if verbose:
        print("The Disimilarity Index is a district minority representation measure. Each index indicates how spread out the minority population is across the district plan.")
        print("Ranges from 0-1, with values closer to 1 indicating higher minority segregation between districts")
    for ethnicity, diss_index in map_one_metrics['Dissimilarity Indices'].items():
        print(f"Dissimilarity index, {eth_common_names[ethnicity]}, for Map One: {diss_index}")
    for ethnicity, diss_index in map_two_metrics['Dissimilarity Indices'].items():
        print(f"Dissimilarity index, {eth_common_names[ethnicity]}, for Map Two: {diss_index}")
    for ethnicity, diss_index in map_one_metrics['Dissimilarity Indices'].items():
        if diss_index < map_two_metrics['Dissimilarity Indices'][ethnicity]:
            print(f"Map One has a better Dissimilarity Index for {eth_common_names[ethnicity]} minority population")
            map_one_winning_metrics.append(f'Dissimilarity Index: {eth_common_names[ethnicity]}')
        elif diss_index > map_two_metrics['Dissimilarity Indices'][ethnicity]:
            print(f"Map Two has a better Dissimilarity Index for {eth_common_names[ethnicity]} minority population")
            map_two_winning_metrics.append(f'Dissimilarity Index: {eth_common_names[ethnicity]}')
        else:
            ties.append(f'Dissimilarity Index: {eth_common_names[ethnicity]}')
            print(f"Both maps have the same Dissimilarity Index for {eth_common_names[ethnicity]}")
    print()

    print("Comparison Summary")
    print("-------------------")
    if len(map_one_winning_metrics) > 0:
        print(f"Map One is better in {len(map_one_winning_metrics)} metrics:")
        print(", ".join(map_one_winning_metrics))
    else:
        print("Map One was not better in any metrics")
    print()

    if (len(map_two_winning_metrics) > 0):
        print(f"Map Two is better in {len(map_two_winning_metrics)} metrics:")
        print(", ".join(map_two_winning_metrics))
    else:
        print("Map Two was not better in any metrics")
    print()

    if len(ties) > 0:
        print(f"There were {len(ties)} ties:")
        print(", ".join(ties))
    else:
        print("There were no ties.")
    print()

    if len(map_one_winning_metrics) > len(map_two_winning_metrics):
        print("Overall, Map One has better metrics")
    elif len(map_one_winning_metrics) < len(map_two_winning_metrics):
        print("Overall, Map Two has better metrics")
    else:
        print("The Maps tied in metric analysis")

    return map_one_winning_metrics, map_two_winning_metrics, ties