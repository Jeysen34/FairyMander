import  geopandas as gpd
from cleancurrent import get_curr_district_file

#import the libarays 

import libpysal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, LineString, Point
from math import pi

class calcMetrics:
    """The reock score finds out if the district is compact or not compact. 
    To define if is compact it will be 1. If it is 0 that means that is not compact.
    To determine the compsite score. Each distict will be meansured by looking at which one is closer to 100%
    """
    #function of the reock score
    def calcRecockScore(testMap):
        #create the crs for the math
        #used the centeral Arizona id
            # We are going to the use the epsg of the centeral of the state
        testMap.to_crs(epsg=26949 , inplace=True)
        # find the geomtry area
        testMap['area'] = testMap['geometry'].area
        # find the miniumun bounding circle
        testMap['MinBoundsCircle'] = testMap.geometry.minimum_bounding_circle()
        #find the area of the min Bounds
        testMap['MinBounds_Area'] = testMap['MinBoundsCircle'].area
        # divide the area to fin the reock score
        testMap['ReockScore'] = testMap['area'] / (testMap['MinBounds_Area'])
        #find the score and time it by 100%
        testMap['ReockScore'] = testMap['ReockScore']*100

    def calcPolsyPopper(testMap):
        """
        This function calcuates the compacts of the distict. It looks at the perimeter and the area of the distict
        Metric 0 - not compact , 1 - compact
        This will be dertmined by looking at the result of the test. One then will determine if it compact if it close to 1
        """
        #Polsby-Popper (4pi * A)/P2
        #A is the area of the district.
        # P is the perimeter of the district.
        #π is the mathematical constant, approximately 3.14159.
        testMap.to_crs(epsg=26949 , inplace=True)
        testMap['Perimeter'] = testMap.geometry.length
        testMap['area'] = testMap['geometry'].area
        # use the equation - convert it int 
        # then times it by 100
        testMap['PolsbyPopper'] = ((((4*pi) * testMap['area'])
                                   / testMap['Perimeter']**2) * 100)
    def calEfficiencyGap(voteMap):
        """ This function will show which party has more favor when it comes to gerrymander.
        Measures propprtionality, this test will look at and see which party is closer to 0.
        If efficiency Gap is postive(+): it means that Party A has gained a advantage through the distict line in there favor. 
        The larger the postive number, the greater the advantage the party
        If efficiency Gap is negaive(-): it means that the that party B benifts from the process. 

       
        #Or take the abst values 
        # (wasted votes for party A - wasted votes for party B) / total votes
        It can  negative a postive as return, you can get a postive or 
        
        """
        #wasted votes Party A
        voteMap['wasteVotesRep'] = voteMap['party_dem'].astype(int)  + voteMap['party_oth'].astype(int)
        
        voteMap['wastedVotesDem']  = voteMap['party_rep'].astype(int) + voteMap['party_oth'].astype(int)
        
         # total votes 
        totalVotes = voteMap['total_reg']

      

        # efficiency gap 
        # the wasted votes of dem is higher so that is first
        #it is rewriteing the efficieny gap, but the problem is that it is not working right when you do it by hand
        voteMap['EfficiencyGap'] = ((( voteMap['wastedVotesDem'] - voteMap['wasteVotesRep'] ) / totalVotes) * 100)
     
    def populationTest(testMap):
        """ This test is just a test to make sure that each district has around the same popluation
        """
        #popluation = state population / number of districts
        #C_TOT22
        #testMap['TotalPopulation'] = testMap.groupby('C_TOT22')

        #testing value, create an error so that make sure that it is a int
        testMap['C_TOT22'] = pd.to_numeric(testMap['C_TOT22'], errors='coerce')
        sumTotal= 0
        # group by district 
        groupedC = testMap.groupby('District')['C_TOT22']

        # check for the each of the value and add them up
        for index, value in groupedC.first().items():
            if pd.notna(value):
                sumTotal += value 

         #find how many disticts are in each state
        totalDistrict = len(testMap.groupby('District'))
        # divide the total / total disticts
        PopulationRule = sumTotal / totalDistrict
        #round the number 
        roundPopulationRule = round(PopulationRule)
        #print out the population
        print("Population Score:",roundPopulationRule)

        #find how many disticts are in each state
        totalDistrict = len(testMap.groupby('District'))
    def meanMedianScore(testMap):
        """Foucus on how the distribution of district vote-shares affects potential seat outcomes,
        calculates the difference between the median and mean vote-share across all districts for one party.
        This looks at which party will have to win votes to see which party is in favor. 
        """
        # mean average party share acrreos all districts
        # find the rep
        meanRep = testMap['party_rep'].mean()
        
        roundMeanRep = round(meanRep)

        # find the dem party mean
        meanGroupDem = testMap['party_dem'].mean()
        
        #round the dem number
        roundMeanDem = round(meanGroupDem)
       

        # find the other party 
        meanGroupOth = testMap['party_oth'].mean()
        #round the number
        roundMeanOth = round(meanGroupOth)
        
        
        # find the median in each party
        # find it in rep party
        meanRepMed = testMap['party_rep'].median()
        roundMedRep = round(meanRepMed)
        
        # find median in dem
        demMed = testMap['party_dem'].median()
        roundMedDem = round(demMed)
        
        # find oth
        othMed = testMap['party_oth'].median()
        roundMedOth = round(othMed)
        
        
        # find the mean_median score
        # find mean_Median score for Rep
        meanMedianRep = roundMeanRep - roundMedRep
        # find the score Dem
        meanMedianDem = roundMeanDem - roundMedDem
        # find the score oth
        meanMedianOth = roundMeanOth - roundMedOth

        print("MeanMedian Repulican Party Score:", meanMedianRep)
        print("MeanMedian Demcratic Party Score:", meanMedianDem)
        print("MeanMedian Other Party Score:", meanMedianOth)

        print("Metric Positive number means positive value for  suggests that the reference party can secure half of the seats with fewer than half of the votes; a negative value suggests that the opposite party has the advantage")
    def lobsidedMagrinScore(testMap):
        """
        This function will determine which party is packed into a district, and will
        see if the party is winning on more distrcist with lower margin vots.
        """
        #print out the Lobsided Margin title
        print("Lobsided Margin Score:")
        #set up the varibles 
        totalMagrinRep = 0
        totalMagrinDem = 0
        totalMagrinOth= 0
        indexRep= 0
        indexDem = 0
       
        indexOth = 0
        # We need to findt the score of percent of each votes
        testMap['RepParty'] = (testMap['party_rep'] / testMap['total_reg'] *100)
        testMap['DemParty'] = (testMap['party_dem'] / testMap['total_reg'] *100)
       
        testMap['OthParty'] = (testMap['party_oth'] / testMap['total_reg'] *100)

        partyGraph = testMap.groupby('District')[['RepParty','DemParty','OthParty']] 
        for index, row in partyGraph.first().iterrows():  # Using .first() to get the first row of each group
            # Store the percentages in a list for comparison
            percentages = [row['RepParty'], row['DemParty'], row['OthParty']]
            parties = ['RepParty', 'DemParty', 'OthParty']
            
            # Find the maximum percentage and corresponding party
            max_value = max(percentages)
            max_index = percentages.index(max_value)
            max_party = parties[max_index]
           # look for the percent of the party. It looks for the highest out of the row,
           # and count it to an index
            if max_party == 'RepParty':
                totalMagrinRep += max_value
                indexRep+= 1
            elif max_party == 'DemParty':
                totalMagrinDem += max_value
                indexDem += 1   
            elif max_value == 'OthParty':
                totalMagrinOth += max_value
                indexOth +=1
                
                    
        if(indexRep > 0):
            percentTotalRep = totalMagrinRep / indexRep
            print("Republican Party Score",percentTotalRep) 

        if(indexDem > 0):
             percentTotalDem = totalMagrinDem/ indexDem  
             print("Democratic Party Score:",percentTotalDem) 
       
        if(indexOth > 0):
            percentTotalOth = totalMagrinOth /indexOth
            print("Other Party score:", percentTotalOth)

        
        if (percentTotalRep > percentTotalDem):
            lobsidedTest = percentTotalRep - percentTotalDem
            print("The Lobsided Margin Score: ",lobsidedTest)
            print("This mean that Republican  party are packed into a few district. Which means the party wins by large margins. The Democratic party on the other hand, is winning substantially more districts with substantially lower vote margins.")
        elif(percentTotalDem > percentTotalRep):
            lobsidedTest = percentTotalDem - percentTotalRep

            print("The Lobsided Margin Score: ",lobsidedTest)
            print("This mean that Democratic party are packed into a few district. Which means the party wins by large margins. The Republican party on the other hand, is winning substantially more districts with substantially lower vote margins.")
        
    def printOutLine(testMap):
        printGraph = testMap.groupby('District')[['ReockScore','PolsbyPopper', 'EfficiencyGap','C_TOT22']]
        print(printGraph.first())

testMap = get_curr_district_file('az')
print(testMap)

ReockScoreRule = calcMetrics.calcRecockScore(testMap)
polsyPopperRule= calcMetrics.calcPolsyPopper(testMap)
efficiencyGapRule= calcMetrics.calEfficiencyGap(testMap)

printOut = calcMetrics.printOutLine(testMap)
popluationRule= calcMetrics.populationTest(testMap)
TestMeanMedian = calcMetrics.meanMedianScore(testMap)
TestLobsided = calcMetrics.lobsidedMagrinScore(testMap)
