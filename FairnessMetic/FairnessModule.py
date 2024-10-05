#import the libarays 

import geopandas as gpd
import libpysal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, LineString, Point
from math import pi

class calcMetrics:
    #function of the reock score
    def calcRecockScore(testMap):
        
        #create the crs for the math
        testMap.to_crs(epsg=3857, inplace=True)
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
       
        #Polsby-Popper (4pi * A)/P2
        #A is the area of the district.
        # P is the perimeter of the district.
        #π is the mathematical constant, approximately 3.14159.
        testMap.to_crs(epsg=3857, inplace=True)
        testMap['Perimeter'] = testMap.geometry.length
        testMap['area'] = testMap['geometry'].area
        # use the equation - convert it int 
        # then times it by 100
        testMap['PolsbyPopper'] = ((((4*pi) * testMap['area'])
                                   / testMap['Perimeter']**2) * 100)
        
        

    def calEfficiencyGap(voteMap):
        # have a check, that finds a which party disticts is higher. which number is hight
        #Or take the abst values 
        # (wasted votes for party A - wasted votes for party B) / total votes
        #wasted votes Party A
        voteMap['wasteVotesRep'] = voteMap['party_dem'].astype(int) + voteMap['party_npp'].astype(int)+ voteMap['party_lib'].astype(int) + voteMap['party_grn'].astype(int) + voteMap['party_oth'].astype(int)
        
        voteMap['wastedVotesDem']  = voteMap['party_rep'].astype(int) +  voteMap['party_npp'].astype(int) + voteMap['party_lib'].astype(int) + voteMap['party_grn'].astype(int) + voteMap['party_oth'].astype(int)
        
         # total votes 
        totalVotes = voteMap['total_reg']

        #had to convert the data to a dataframe
        df = pd.DataFrame({'Rep': voteMap['wasteVotesRep'],'Dem':voteMap['wastedVotesDem'], 'totalVotesRow':voteMap['total_reg'].astype(int)})
        #loop through the rows
        for index, row in df.iterrows():
            #check if the rep number is hight than dem
            if(row['Rep'] > row['Dem']):
                #use equation to find gap
                newRow = ( row['Rep'] - row['Dem'] )
                nameCallTwo= (( newRow / totalVotes)*100)
            #check if dem is higher than rep
            elif(row['Rep'] < row['Dem']):
               # set equation
               nameCallTwo = ((( row['Dem'] - row['Rep'] ) / totalVotes)*100)

            print(row['Rep'], row['Dem'],row['totalVotesRow'])
        voteMap['EfficiencyGap'] = nameCallTwo
        print(nameCallTwo)
           #NOT working somehting in the loop is wrong 
        #print out the grouped by districts it is see the data as a whole.
        printGraph = voteMap.groupby('District')[['wasteVotesRep', 'wastedVotesDem','total_reg','EfficiencyGap']]
        print(printGraph.first())

        # efficiency gap 
        # the wasted votes of dem is higher so that is first
        #it is rewriteing the efficieny gap, but the problem is that it is not working right when you do it by hand
        voteMap['EfficiencyGap'] = ((( voteMap['wastedVotesDem'] - voteMap['wasteVotesRep'] ) / totalVotes) * 100)
     
        
   

    def popluationTest(testMap):
        #popluation = state population / number of districts
        #C_TOT22	
        #testMap['TotalPopulation'] = testMap.groupby('C_TOT22')

        #testing value
        groupedC = testMap.groupby('District')['C_TOT22']
        #Sum of estimate popluation
        totalPop = testMap['C_TOT22'].sum()
        #find how many disticts are in each state
        totalDistrict = len(testMap.groupby('District'))

        PopulationEqu = totalPop/ totalDistrict
        popluationInt = PopulationEqu.astype(int)
        #This is the popluation in each distict that each distict should have
        print("Popluation of each distict should be around: ", popluationInt)
    def meanMedianScore(testMap):
        # mean average party share acrreos all districts
        totalDistrict = len(testMap.groupby('District'))
        #add all the districts up
        sumOfPatryRep =testMap['party_rep'].sum
        print(sumOfPatryRep)
        #mean = sumOfPatryRep/totalDistrict

        meann = testMap['party_dem'].astype(int) + testMap['party_npp'].astype(int)+ testMap['party_lib'].astype(int) + testMap['party_grn'].astype(int) + testMap['party_oth'].astype(int)
        #divide by number of disticts to get the averge of each district
      
        
        #find the median 
        # line up lowest to highest for votes in each disticts
        # find the middle 
       
        
        groupM = testMap['party_rep'].median()
        #meanMedianType = mean - groupM
        #print(meanMedianType)
   

        

    def compositeScore(testMap):

        # ceate a score indes
        score = 0
        scoreGap = 0
        scorePopper = 0
        grouped = testMap.groupby('District')
        
        zero = grouped['ReockScore'].apply(lambda x: (x== 0.0).any())
        for x in zero:
            if(x == True):
                score = score +1
        

        popperScore = grouped['PolsbyPopper'].apply(lambda x: (x== 0).any())
        for scoreOfPop in popperScore:
            if(scoreOfPop == True):
                scorePopper = scorePopper +1
        gapFilter = grouped['EfficiencyGap']
       #print(gapFilter.first())
        # trying to list throught the efficiency gap

        

        # NOTE: Consider using wieghted averge
       
     

        # With the voting data, use the reg parties
        # use the mean- medium, and lobsided test
        # comment 
        # percent of the 

        
        print("Score of ReockScore:", score) 
        print("Score of Efficiency Gap:", scoreGap)
        print("Score of the Polsby Popper:", scorePopper)     

    def  mintioryMajor(testMap):
        #Majority rule means that the candidate or choice receiving more than 50% of all the votes is the winner.
        # we are going to convert it to see if rep or other partys have 50%
        # frist we need to know the score of register of the party into percent 
       demPercent =  testMap['party_dem'] / testMap['total_reg'] *100
       #print(demPercent)
       repPerecent = testMap['party_rep'] / testMap['total_reg'] *100
       #print(repPerecent)
       nppPerecent = testMap['party_npp'] / testMap['total_reg'] * 100
       libPerecent = testMap['party_lib'] / testMap['total_reg'] * 100
       grnPerecent = testMap['party_grn'] / testMap['total_reg'] * 100
       othPerecent = testMap['party_oth'] / testMap['total_reg'] * 100
       #print(nppPerecent, libPerecent, grnPerecent,othPerecent)
       # look through each of them to check if they have more than 50% 
       # and if they have more than 50 the minoty win. 
       #if the have less than 50% they have a mintoy
       #I am not sure what we are doing minoty votes or popluation 
      

    def printoutGraph(testMap):
        #print out the findings
        printGraph = testMap.groupby('District')[['ReockScore','PolsbyPopper','EfficiencyGap']]
        print(printGraph.first())

       


#grab the test files
     
filePath = "/Users/ceannajarrett/Documents/GitHub/FairyMander/Data/DistrictShpFiles/AZ/az_districts.shp"

testMap = gpd.read_file(filePath) 

efficiencyGapRule= calcMetrics.calEfficiencyGap(testMap)
ReockScoreRule = calcMetrics.calcRecockScore(testMap)
polsyPopperRule= calcMetrics.calcPolsyPopper(testMap)
MetricsPrintOut= calcMetrics.printoutGraph(testMap)
popluationRule= calcMetrics.popluationTest(testMap)
compsiteRule = calcMetrics.compositeScore(testMap)
TestMajorMintory = calcMetrics.mintioryMajor(testMap)
TestMeanMedian = calcMetrics.meanMedianScore(testMap)




