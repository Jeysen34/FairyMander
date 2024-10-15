#!/usr/bin/env python
# coding: utf-8

import geopandas as gpd
import pandas as pd
from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
from gerrychain import (GeographicPartition, Graph, MarkovChain,
                        updaters, constraints, accept)
import matplotlib.pyplot as plt
from gerrychain.metrics import polsby_popper
from gerrychain import updaters, constraints, accept
from gerrychain.tree import bipartition_tree
from gerrychain.proposals import recom
from gerrychain.constraints import contiguous, within_percent_of_ideal_population, Validator
from functools import partial
from gerrychain.optimization import SingleMetricOptimizer
import random
from multiprocessing import Pool


class DistrictGenerator:
    def __init__(self, prefix, deviation, steps, numMaps, toShpFileFlag):
        
        # initialize with user input
        self.prefix = prefix
        self.steps = steps
        self.numMaps = numMaps
        #self.numDisplayMaps = numDisplayMaps
        self.deviation = deviation
        self.toShpFileFlag = toShpFileFlag
        self.numDistricts = {
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

    # function to get state shapefile
    def get_state_gdf(self):
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
        geo_df = gpd.read_file(f"./stateShapefiles/{self.prefix}_cvap_2022_t/{self.prefix}_cvap_2022_t.shp")
        voting_df = pd.read_csv(f"./CSVfiles/st{id_map[self.prefix]}_{self.prefix}_new.csv", delimiter=",", header=0, dtype={'GEOID20': str})
        return geo_df[['GEOID20', 'geometry', 'C_TOT22']].merge(voting_df, on='GEOID20')

    

    def get_random_partition(self):
        # get the state's merged shapefile
        state_gdf = self.get_state_gdf()

        state_graph = Graph.from_geodataframe(state_gdf)

        partition_updaters = {
            "population": updaters.Tally("C_TOT22"),
            "cut_edges": updaters.cut_edges,
            "polsby-popper": polsby_popper
        }
        return GeographicPartition.from_random_assignment(state_graph, self.numDistricts[self.prefix], self.deviation, 'C_TOT22', updaters=partition_updaters)



    def generate_map(self, initial_partition):
        opt_metric = lambda x: sum(x["polsby-popper"].values())/len(x)

        ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)

        # this is to be used by the loop below, it determines when to save a map
        save_map = self.steps // self.numMaps

        proposal = partial(
            recom,
            pop_col="C_TOT22",
            pop_target=ideal_population,
            epsilon=self.deviation,
            node_repeats=2,
            method = partial(
                bipartition_tree,
                max_attempts=10000,
                allow_pair_reselection=True
            )
        )

        recom_chain = SingleMetricOptimizer(
            initial_state=initial_partition,
            proposal=proposal,
            constraints=[contiguous],
            optimization_metric=opt_metric,
            maximize=True,
        )

        best = []

        for i, item in enumerate(recom_chain.simulated_annealing(
            self.steps + 1,
            recom_chain.jumpcycle_beta_function(200,800),
            beta_magnitude=1,
        )):
            print(f"Finished step {i+1}/{self.steps}", end="\r")
            if i % save_map == 0 and i > 0:
                # NOTE: I am appending the current best partition to our result array, but we may just want to return the final best map...thoughts?
                best.append(recom_chain.best_part.assignment)

        return best

    # fairness tests temp stub

    def run(self):
        index = 0
        print("\ngetting state GeoDataFrame")
        state_gdf = self.get_state_gdf()
        if self.prefix == 'ca':
            state_gdf = state_gdf[~state_gdf['GEOID20'].isin({'06075980401', '06037599000', '06037599100'})]
        elif self.prefix == 'fl':
            state_gdf = state_gdf[~state_gdf['GEOID20'].isin({'12087980100'})]
        elif self.prefix == 'ny':
            state_gdf = state_gdf[~state_gdf['GEOID20'].isin({'36061000100'})]
        # NOTE: need to have consistent EPSG's we use for each state....not strictly necessary to implement right now but might want to communicate w/ Ceanna about how we want to set up a file to keep track of which epsg to use for which state.
        # 32116 AZ epsg = 26912
        state_gdf.to_crs(epsg=26912, inplace=True)
        print("getting state partition")
        init_partition=self.get_random_partition()
        print("generating map")
        best = self.generate_map(init_partition)

        for final in best:
            state_gdf['District'] = state_gdf.index.map(final)
            # Group by 'District' and sum the population
            district_population = state_gdf.groupby('District')['C_TOT22'].sum()

            # Print the population of each district
            print("Population in each district:")
            print(district_population)

            # Visualize the result
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            state_gdf.plot(column='District', ax=ax, legend=True, cmap="rainbow")
            plt.title("District Assignment from Markov Chain ReCom")
            plt.show()

            # save the results as a shapefile if the user specified to
            if self.toShpFileFlag == "yes":
                state_gdf.to_file(f"./districtShpFiles/{self.prefix}_districts{index}.shp")
                index += 1
            
