#import the libarays 

import geopandas as gpd
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
        voteMap['wasteVotesRep'] = voteMap['party_dem'].astype(int) + voteMap['party_npp'].astype(int)+ voteMap['party_lib'].astype(int) + voteMap['party_grn'].astype(int) + voteMap['party_oth'].astype(int)
        
        voteMap['wastedVotesDem']  = voteMap['party_rep'].astype(int) +  voteMap['party_npp'].astype(int) + voteMap['party_lib'].astype(int) + voteMap['party_grn'].astype(int) + voteMap['party_oth'].astype(int)
        
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
        
        #finf the nnp
        meanGroupNpp = testMap['party_npp'].mean()
        roundMeanNpp = round(meanGroupNpp)

        #find the lib
        meanGroupLib = testMap['party_lib'].mean()
        roundMeanLib = round(meanGroupLib)
        # find the grn
        meanGroupGrn = testMap['party_grn'].mean()
        roundMeanGrn = round(meanGroupGrn)
        
        # find the other party - add all the other partys
        testMap['meanGroupOth'] = testMap['party_oth'] + testMap['party_npp'] + testMap['party_grn'] + testMap['party_lib']
        #round the number, find the mean of all the parties
        meanGroupOth = testMap['meanGroupOth'].mean()
        roundMeanOth = round(meanGroupOth)
        
        
        # find the median in each party
        # find it in rep party
        meanRepMed = testMap['party_rep'].median()
        roundMedRep = round(meanRepMed)
        
        # find median in dem
        demMed = testMap['party_dem'].median()
        roundMedDem = round(demMed)
        
        # find oth
        othMed = testMap['meanGroupOth'].median()
        roundMedOth = round(othMed)
        
        
        # find the mean_median score
        # find mean_Median score for Rep
        meanMedianRep = roundMeanRep - roundMedRep
        # find the score Dem
        meanMedianDem = roundMeanDem - roundMedDem
        # find the score oth
        meanMedianOth = roundMeanOth - roundMedOth
     

        print("MeanMedian Republican Party Score:", meanMedianRep)
        print("MeanMedian Democratic Party Score:", meanMedianDem)
   
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
        totalMagrinNpp = 0
        totalMagrinGrn = 0
        totalMagrinLib = 0
        totalMagrinOth= 0
        indexRep= 0
        indexDem = 0
        indexNpp= 0
        indexGrn = 0
        indexlib = 0
        indexOth = 0
        # We need to findt the score of percent of each votes
        testMap['RepParty'] = (testMap['party_rep'] / testMap['total_reg'] *100)
        testMap['DemParty'] = (testMap['party_dem'] / testMap['total_reg'] *100)
        # find the score of all the other parties
        testMap['OthParty'] = ((testMap['party_oth'] + testMap['party_grn'] + testMap['party_lib'] + testMap['party_npp'] )/ testMap['total_reg'] *100)

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
                
        #check if index is creater than 0             
        if(indexRep > 0):
            percentTotalRep = totalMagrinRep / indexRep
            print("Republican Party Score",percentTotalRep) 
        # look for the dem index
        if(indexDem > 0):
             percentTotalDem = totalMagrinDem/ indexDem  
             print("Democratic Party Score:",percentTotalDem) 
        # looking for the index of all the partys
        if(indexOth > 0):
            percentTotalOth = totalMagrinOth /indexOth
            print("Other Party score:", percentTotalOth)

        # check if the total bigger, than it prints the lobsided test
        if (percentTotalRep > percentTotalDem):
            lobsidedTest = percentTotalRep - percentTotalDem
            print("The Lobsided Margin Score: ",lobsidedTest)
            print("This mean that Republican  party are packed into a few district. Which means the party wins by large margins. The Democratic party on the other hand, is winning substantially more districts with substantially lower vote margins.")
        elif(percentTotalDem > percentTotalRep):
            lobsidedTest = percentTotalDem - percentTotalRep

            print("The Lobsided Margin Score: ",lobsidedTest)
            print("This mean that Democratic party are packed into a few district. Which means the party wins by large margins. The Republican party on the other hand, is winning substantially more districts with substantially lower vote margins.")
        
       
        
     
       

        

       
    #def  mintioryMajor(testMap):
        #Majority rule means that the candidate or choice receiving more than 50% of all the votes is the winner.
        # we are going to convert it to see if rep or other partys have 50%
        # frist we need to know the score of register of the party into percent 
      # demPercent =  testMap['party_dem'] / testMap['total_reg'] *100
       #print(demPercent)
       #repPerecent = testMap['party_rep'] / testMap['total_reg'] *100
       #print(repPerecent)
       #nppPerecent = testMap['party_npp'] / testMap['total_reg'] * 100
       #libPerecent = testMap['party_lib'] / testMap['total_reg'] * 100
       #grnPerecent = testMap['party_grn'] / testMap['total_reg'] * 100
       #othPerecent = testMap['party_oth'] / testMap['total_reg'] * 100
       #print(nppPerecent, libPerecent, grnPerecent,othPerecent)
       # look through each of them to check if they have more than 50% 
       # and if they have more than 50 the minoty win. 
       #if the have less than 50% they have a mintoy
       #I am not sure what we are doing minoty votes or popluation 
      
    def printOutLine(testMap):
        #print out the data for each district
        printGraph = testMap.groupby('District')[['ReockScore','PolsbyPopper', 'EfficiencyGap','C_TOT22']]
        print(printGraph.first())
    


#grab the test files
     
filePath = "shapeFile/AZ/az_districts.shp"

testMap = gpd.read_file(filePath) 


efficiencyGapRule= calcMetrics.calEfficiencyGap(testMap)
ReockScoreRule = calcMetrics.calcRecockScore(testMap)
polsyPopperRule= calcMetrics.calcPolsyPopper(testMap)


#TestMajorMintory = calcMetrics.mintioryMajor(testMap)


printOut = calcMetrics.printOutLine(testMap)
popluationRule= calcMetrics.populationTest(testMap)
TestLobsided = calcMetrics.lobsidedMagrinScore(testMap)
TestMeanMedian = calcMetrics.meanMedianScore(testMap)



