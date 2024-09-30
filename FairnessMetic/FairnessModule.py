#import the libarays 
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
        testMap['ReockScore'] = testMap['ReockScore'].astype(int)
       

    def calcPolsyPopper(testMap):
       
        #Polsby-Popper (4pi * A)/P2
        #A is the area of the district.
        # P is the perimeter of the district.
        #π is the mathematical constant, approximately 3.14159.
        testMap.to_crs(epsg=3857, inplace=True)
        testMap['Perimeter'] = testMap.geometry.length
        testMap['area'] = testMap['geometry'].area
        # use the equation - convert it int
        testMap['PolsbyPopper'] = (((4*pi) * testMap['area'])
                                   / testMap['Perimeter']**2).astype(int)
        

    def calEfficiencyGap(voteMap):
        # (wasted votes for party A - wasted votes for party B) / total votes
        #wasted votes Party A
        voteMap['wasteVotesRep'] = voteMap['party_dem'].astype(int) + voteMap['party_npp'].astype(int)+ voteMap['party_lib'].astype(int) + voteMap['party_grn'].astype(int) + voteMap['party_oth'].astype(int)
        
        voteMap['wastedVotesDem']  = voteMap['party_rep'].astype(int) +  voteMap['party_npp'].astype(int) + voteMap['party_lib'].astype(int) + voteMap['party_grn'].astype(int) + voteMap['party_oth'].astype(int)
        
         # total votes 
        totalVotes = voteMap['total_reg'].astype(int)
        # efficiency gap 
        # the wasted votes of dem is higher so that is first
        voteMap['EfficiencyGap'] = (( voteMap['wastedVotesDem'] - voteMap['wasteVotesRep'] ) / totalVotes)
        voteMap['PercentGap'] = voteMap['EfficiencyGap'] * 100
        
    def printoutGraph(testMap):
        #print out the findings
        printGraph = testMap.groupby('District')[['ReockScore','PolsbyPopper','EfficiencyGap','PercentGap']]
        print(printGraph.first())

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
    

    def compositeScore(testMap):

        # ceate a score indes
        score = 0
        scoreGap = 0
        scorePopper = 0
        grouped = testMap.groupby('District')
        
        zero = grouped['ReockScore'].apply(lambda x: (x== 0).any())
        for x in zero:
            if(x == True):
                score = score +1
        

        popperScore = grouped['PolsbyPopper'].apply(lambda x: (x== 0).any())
        for scoreOfPop in popperScore:
            if(scoreOfPop == True):
                scorePopper = scorePopper +1
        gapFilter = grouped['EfficiencyGap']
        print(gapFilter.first())
        # trying to list throught the efficiency gap
       
     

        
        
      
            
        
        print("Score of ReockScore:", score) 
        print("Score of Efficiency Gap:", scoreGap)
        print("Score of the Polsby Popper:", scorePopper)       
        
                
            
        
       

        



        

#grab the test files
     
filePath = "/Users/ceannajarrett/Documents/GitHub/FairyMander/Data/DistrictShpFiles/AZ/az_districts.shp"

testMap = gpd.read_file(filePath) 

efficiencyGapRule= calcMetrics.calEfficiencyGap(testMap)
ReockScoreRule = calcMetrics.calcRecockScore(testMap)
polsyPopperRule= calcMetrics.calcPolsyPopper(testMap)
MetricsPrintOut= calcMetrics.printoutGraph(testMap)
popluationRule= calcMetrics.popluationTest(testMap)
compsiteRule = calcMetrics.compositeScore(testMap)




