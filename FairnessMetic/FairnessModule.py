#import the libarays 

import geopandas as gpd
import numpy as np
import pandas as pd
from math import pi, ceil
from statistics import median
import matplotlib.pyplot as plt


eth_common_names = {
    'eth1_aa': 'African American',
    'eth1_esa': 'East and South Asian',
    'eth1_hisp': 'Hispanic',
    'eth1_oth': 'Other'
}

"""
Class of functions for performing district fairness calculations
Make sure you have dissolved the map before using this module, i.e. the map should
be of the districts and not of the tracts assigned to the districts
"""
def get_metric_dict(test_map):
    result_dict = {
            'Avg Polsby-Popper': calc_avg_polsby_popper(test_map),
            'Avg Reock': calc_avg_reock(test_map),
            'Efficiency Gap': calc_efficiency_gap(test_map),
            'Mean Median Difference': calc_mean_median_difference(test_map),
            'Lobsided Margin': calc_lobsided_margins(test_map),
            'Dissimilarity Indices': calc_dissimilarity_index(test_map)
    }

    return result_dict

def full_analysis(test_map, verbose = False, showMap = True):
    if showMap:
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        test_map.plot(column='District', ax=ax, legend=True, cmap="rainbow")
        plt.title("District Map")
        plt.show()
    print("Running Fairness Analysis")
    print("-------------------------")
    if verbose:
        print("The Polsby-Popper Score is a district compactness measure. It is the ratio between a district's area and its perimeter.")
        print("Ranges from 0-1, with values closer to 1 meaning higher comapctness")
    print(f"Average Polsby-Popper Score: {calc_avg_polsby_popper(test_map)}")
    print()
    if verbose:
        print("The Reock Score is a district compactness measure. It is the ratio between a district's area and the area of a minimum bounding circle around the district.")
        print("Ranges from 0-1, with values closer to 1 meaning higher comapctness")
    print(f"Average Reock Score: {calc_avg_reock(test_map)}")
    print()
    if verbose:
        print("The Efficiency Gap is a district competitiveness measure. It uses wasted votes in an election (i.e., votes that didn't contribute to the election outcome) to quantify partisanship")
        print("A negative (-) value indicates a Democrat advantage, while a positive (+) value indicates a Republican advantage")
    print(f"Efficiency Gap: {calc_efficiency_gap(test_map)}")
    print()
    if verbose:
        print("The Mean Median Difference is a district competitiveness measure. It is the difference between a party's average vote share and its median vote share across all districts")
        print("A percent difference, with a negative (-) value indicates a Democrat advantage, while a positive (+) value indicates a Republican advantage")
    print(f"Mean Median Difference: {calc_mean_median_difference(test_map)}")
    print()
    if verbose:
        print("The Lobsided Margin test is a district competitiveness measure. It is the difference between the average percentages by which each party won in a district.")
        print("A percent difference, where a negative (-) value indicates Republicans have been packed (i.e., a Democrat advantage), where a positive (+) value indicates Democrats have been packed (i.e., a Republican advantage")
    print(f"Lobsided Margin Score: {calc_lobsided_margins(test_map)}")
    print()
    if verbose:
        print("The Disimilarity Index is a district minority representation measure. Each index indicates how spread out the minority population is across the district plan.")
        print("Ranges from 0-1, with values closer to 1 indicating higher minority segregation between districts")
    diss_index_res = calc_dissimilarity_index(test_map)
    for ethnicity, diss_index in diss_index_res.items():
        print(f"Dissimilarity index, {eth_common_names[ethnicity]}: {diss_index}")
    print()


def compare_maps(map_one, map_two, verbose=False, showMaps = True):
    if showMaps:
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
        print("A negative (-) value indicates a Democrat advantage, while a positive (+) value indicates a Republican advantage")
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
        print("A percent difference, with a negative (-) value indicates a Democrat advantage, while a positive (+) value indicates a Republican advantage")
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
        print("The Lobsided Margin test is a district competitiveness measure. It is the difference between the average percentages by which each party won in a district.")
        print("A percent difference, where a negative (-) value indicates Republicans have been packed (i.e., a Democrat advantage), where a positive (+) value indicates Democrats have been packed (i.e., a Republican advantage")
    print(f"Lobsided Margin Score, Map One: {map_one_metrics['Lobsided Margin']}")
    print(f"Lobsided Margin Score, Map Two: {map_two_metrics['Lobsided Margin']}")
    if abs(map_one_metrics['Lobsided Margin']) < abs(map_two_metrics['Lobsided Margin']):
        print("Map One has a better Lobsided Margin Score")
        map_one_winning_metrics.append('Lobsided Margin')
    elif abs(map_one_metrics['Lobsided Margin']) > abs(map_two_metrics['Lobsided Margin']):
        print("Map Two has a better Lobsided Margin Score")
        map_two_winning_metrics.append('Lobsided Margin')
    else:
        ties.append('Lobsided Margin')
        print("Both maps have the same Lobsided Margin Score")
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
    print(f"Map One is better in {len(map_one_winning_metrics)} metrics:")
    print(", ".join(map_one_winning_metrics))
    print()
    print(f"Map Two is better in {len(map_two_winning_metrics)} metrics:")
    print(", ".join(map_two_winning_metrics))
    if len(ties) > 0:
        print(f"There were {len(ties)} ties:")
        print(", ".join(map_two_winning_metrics))
    print()

    if len(map_one_winning_metrics) > len(map_two_winning_metrics):
        print("Overall, Map One has better metrics")
    elif len(map_one_winning_metrics) < len(map_two_winning_metrics):
        print("Overall, Map Two has better metrics")
    else:
        print("The Maps tied in metric analysis")


#function of the reock score
def calc_avg_reock(test_map):
    """
    The reock score finds out if the district is compact or not compact.
    The score ranges from 0-1, with values closer to 1 indicating compactness
    """

    # get the number of districts, in this case the number of rows in the map
    num_districts = test_map.shape[0]

    # get the minimum bounded circles
    min_bounding_circles = test_map.minimum_bounding_circle()

    # init average reock score
    average_reock_score = 0

    # get the average reock score for each district
    for district_num in range(0, num_districts):
        district_area = test_map.loc[district_num, 'geometry'].area
        min_bounding_circle_area = min_bounding_circles[district_num].area
        average_reock_score += district_area / min_bounding_circle_area

    return average_reock_score / num_districts

def calc_avg_polsby_popper(test_map):
    """
    The pollsby popper score calcuates the compactness of the district. It is a ratio between the perimeter 
    and the area of the distict
    The score ranges from 0-1, with values closer to 1 indicating compactness
    """
    #Polsby-Popper (4pi * A)/P2
    #A is the area of the district.
    # P is the perimeter of the district.
    #π is the mathematical constant, approximately 3.14159.

    # get the number of districts, in this case the number of rows in the map
    num_districts = test_map.shape[0]

    # init average pp score
    avg_pp_score = 0

    for district_num in range(num_districts):
        district_area = test_map.loc[district_num, 'geometry'].area
        district_perimeter = test_map.loc[district_num, 'geometry'].length
        avg_pp_score += (4 * np.pi) * (district_area / (district_perimeter ** 2))

    return avg_pp_score / num_districts


def calc_efficiency_gap(test_map):
    """ This function will show which party has more favor when it comes to gerrymander.
    Measures propprtionality, this test will look at and see which party is closer to 0.
    If efficiency Gap is postive(+): it means that Party A has gained a advantage through the distict line in there favor. 
    The larger the postive number, the greater the advantage the party
    If efficiency Gap is negaive(-): it means that the that party B benifts from the process. 


    #Or take the abst values
    # (wasted votes for party A - wasted votes for party B) / total votes
    It can  negative a postive as return, you can get a postive or
    """
    wasted_votes_rep = 0
    wasted_votes_dem = 0
    total_votes = 0

    for _, district in test_map.iterrows():
        district_votes = district['party_rep'] + district['party_dem']
        total_votes += district_votes
        votes_to_win = ceil(district_votes / 2)
        if district['party_rep'] > district['party_dem']:
            wasted_votes_dem += district['party_dem']
            wasted_votes_rep += district['party_rep'] - votes_to_win
        else:
            wasted_votes_rep += district['party_rep']
            wasted_votes_dem += district['party_dem'] - votes_to_win

    return ((wasted_votes_dem - wasted_votes_rep) / total_votes) * 100

def populationTest(testMap):
    """ This test is just a test to make sure that each district has around the same popluation
    """
    #popluation = state population / number of districts
    #C_TOT22	
    #testMap['TotalPopulation'] = testMap.groupby('C_TOT22')
    
    testMap['C_TOT22'] = pd.to_numeric(testMap['C_TOT22'], errors='coerce')
    #testing value
    
    sumTotal= 0
    groupedC = testMap.groupby('District')['C_TOT22']
    for index, value in groupedC.first().items():
            if pd.notna(value):
                sumTotal += value 
    
    
    #find how many disticts are in each state
    totalDistrict = len(testMap.groupby('District'))
    

    PopulationRule = sumTotal / totalDistrict
    roundPopulationRule = round(PopulationRule)
    print("Population Score:",roundPopulationRule)
    
def calc_mean_median_difference(test_map):
    """Foucus on how the distribution of district vote-shares affects potential seat outcomes,
    calculates the difference between the median and mean vote-share across all districts for one party.
    This looks at which party will have to win votes to see which party is in favor. 
    """
    dem_percentages = []
    total_votes = 0

    for _, district in test_map.iterrows():
        district_votes = district['party_rep'] + district['party_dem']
        total_votes += district_votes
        dem_percentages.append(district['party_dem'] / district_votes)

    dem_percentage_statewide = test_map['party_dem'].sum() / total_votes

    return 100 * (dem_percentage_statewide - median(dem_percentages))

    # # mean average party share acrreos all districts
    # # find the rep
    # meanRep = testMap['party_rep'].mean()
    # roundMeanRep = round(meanRep)

    # # find the dem party mean
    # meanGroupDem = testMap['party_dem'].mean()
    # #round the dem number
    # roundMeanDem = round(meanGroupDem)
    
    # #finf the nnp
    # meanGroupNpp = testMap['party_npp'].mean()
    # roundMeanNpp = round(meanGroupNpp)

    # #find the lib
    # meanGroupLib = testMap['party_lib'].mean()
    # roundMeanLib = round(meanGroupLib)
    # # find the grn
    # meanGroupGrn = testMap['party_grn'].mean()
    # roundMeanGrn = round(meanGroupGrn)
    
    # # find the other party - add all the other partys
    # testMap['meanGroupOth'] = testMap['party_oth'] + testMap['party_npp'] + testMap['party_grn'] + testMap['party_lib'] + testMap['party_unk']
    # #round the number, find the mean of all the parties
    # meanGroupOth = testMap['meanGroupOth'].mean()
    # roundMeanOth = round(meanGroupOth)
    
    
    # # find the median in each party
    # # find it in rep party
    # meanRepMed = testMap['party_rep'].median()
    # roundMedRep = round(meanRepMed)
    
    # # find median in dem
    # demMed = testMap['party_dem'].median()
    # roundMedDem = round(demMed)
    
    # # find oth
    # othMed = testMap['meanGroupOth'].median()
    # roundMedOth = round(othMed)
    
    
    # # find the mean_median score
    # # find mean_Median score for Rep
    # meanMedianRep = roundMeanRep - roundMedRep
    # # find the score Dem
    # meanMedianDem = roundMeanDem - roundMedDem
    # # find the score oth
    # meanMedianOth = roundMeanOth - roundMedOth
    

    # print("MeanMedian Republican Party Score:", meanMedianRep)
    # print("MeanMedian Democratic Party Score:", meanMedianDem)

    # print("MeanMedian Other Party Score:", meanMedianOth)
    

    # print("Metric Positive number means positive value for  suggests that the reference party can secure half of the seats with fewer than half of the votes; a negative value suggests that the opposite party has the advantage")

def calc_lobsided_margins(test_map):
    """
    This function will determine which party is packed into a district, and will
    see if the party is winning on more distrcist with lower margin vots. 
    """
    dem_win_percents = []
    rep_win_percents = []
    for _, district in test_map.iterrows():
        district_votes = district['party_rep'] + district['party_dem']
        if district['party_rep'] > district['party_dem']:
            rep_win_percents.append((district['party_rep'] / district_votes) * 100)
        else:
            dem_win_percents.append((district['party_dem'] / district_votes) * 100)
    return  (sum(dem_win_percents) / len(dem_win_percents)) - (sum(rep_win_percents) / len(rep_win_percents))


    # #print out the Lobsided Margin title
    # print("Lobsided Margin Score:")
    # #set up the varibles 
    # totalMagrinRep = 0
    # totalMagrinDem = 0
    # totalMagrinNpp = 0
    # totalMagrinGrn = 0
    # totalMagrinLib = 0
    # totalMagrinOth= 0
    # indexRep= 0
    # indexDem = 0
    # indexNpp= 0
    # indexGrn = 0
    # indexlib = 0
    # indexOth = 0
    # # We need to findt the score of percent of each votes
    # testMap['RepParty'] = (testMap['party_rep'] / testMap['total_reg'] *100)
    # testMap['DemParty'] = (testMap['party_dem'] / testMap['total_reg'] *100)
    # # find the score of all the other parties
    # testMap['OthParty'] = ((testMap['party_oth'] + testMap['party_grn'] + testMap['party_lib'] + testMap['party_npp'] + testMap['party_unk'] )/ testMap['total_reg'] *100)

    # partyGraph = testMap.groupby('District')[['RepParty','DemParty','OthParty']] 
    # for index, row in partyGraph.first().iterrows():  # Using .first() to get the first row of each group
    #     # Store the percentages in a list for comparison
    #     percentages = [row['RepParty'], row['DemParty'], row['OthParty']]
    #     parties = ['RepParty', 'DemParty', 'OthParty']
        
    #     # Find the maximum percentage and corresponding party
    #     max_value = max(percentages)
    #     max_index = percentages.index(max_value)
    #     max_party = parties[max_index]
    #    # look for the percent of the party. It looks for the highest out of the row,
    #    # and count it to an index
    #     if max_party == 'RepParty':
    #         totalMagrinRep += max_value
    #         indexRep+= 1
    #     elif max_party == 'DemParty':
    #         totalMagrinDem += max_value
    #         indexDem += 1   
    #     elif max_value == 'OthParty':
    #         totalMagrinOth += max_value
    #         indexOth +=1
            
    # #check if index is creater than 0
    # if(indexRep > 0):
    #     percentTotalRep = totalMagrinRep / indexRep
    #     print("Republican Party Score",percentTotalRep) 
    # # look for the dem index
    # if(indexDem > 0):
    #      percentTotalDem = totalMagrinDem/ indexDem  
    #      print("Democratic Party Score:",percentTotalDem) 
    # # looking for the index of all the partys
    # if(indexOth > 0):
    #     percentTotalOth = totalMagrinOth /indexOth
    #     print("Other Party score:", percentTotalOth)

    # # check if the total bigger, than it prints the lobsided test
    # if (percentTotalRep > percentTotalDem):
    #     lobsidedTest = percentTotalRep - percentTotalDem
    #     print("The Lobsided Margin Score: ",lobsidedTest)
    #     print("This mean that Republican  party are packed into a few district. Which means the party wins by large margins. The Democratic party on the other hand, is winning substantially more districts with substantially lower vote margins.")
    # elif(percentTotalDem > percentTotalRep):
    #     lobsidedTest = percentTotalDem - percentTotalRep

    #     print("The Lobsided Margin Score: ",lobsidedTest)
    #     print("This mean that Democratic party are packed into a few district. Which means the party wins by large margins. The Republican party on the other hand, is winning substantially more districts with substantially lower vote margins.")

def calc_dissimilarity_index(test_map):
    # make list of demographic headers
    demographics = ['eth1_hisp', 'eth1_aa','eth1_esa', 'eth1_oth']
    tot_white_pop = test_map['eth1_eur'].sum()
    num_districts = test_map.shape[0]
    dis_indices = {}

    for demographic in demographics:
        tot_minority_pop = test_map[demographic].sum()
        dis_index = 0

        for district_num in range(num_districts):
            district_white_pop = test_map.loc[district_num, 'eth1_eur']
            district_minority_pop = test_map.loc[district_num, demographic]
            dis_index += abs((district_minority_pop / tot_minority_pop) - (district_white_pop / tot_white_pop))

        dis_index *= 1/2

        dis_indices[demographic] = dis_index
    return dis_indices

# # Usage example
# file_path = "shapeFile/AZ/az_districts.shp"

# test_map_ex = gpd.read_file(file_path)
# test_map_ex = test_map_ex.dissolve(by='District', aggfunc='sum')
# test_map_curr = get_curr_district_file('az')
# full_analysis(test_map_ex)
# compare_maps(test_map_ex, test_map_curr)