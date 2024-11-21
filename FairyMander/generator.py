import geopandas as gpd
from gerrychain import (GeographicPartition, Graph, updaters)
import matplotlib.pyplot as plt
from gerrychain.metrics import polsby_popper
from gerrychain.tree import bipartition_tree
from gerrychain.proposals import recom
from gerrychain.constraints import contiguous
from functools import partial
from fairymander.data import num_districts, epsg
from gerrychain.optimization import SingleMetricOptimizer
from typing import Tuple
import heapq
import os
import importlib.util

class DistrictGenerator:
    """
    Generator class for managing district generation and outputting districts

    Attributes
    ----------
    prefix : string
        the two letter state abbreviation (i.e. az, ut, ny, etc.)
    deviation : float
        the acceptable population defiation between districts (i.e. 0.05 for 5% population deviation)
    steps : int
        the number of steps to run the algorithm for, allowing it to further explore the possible maps
    num_maps : int
        the number of maps to keep, keeps the top (num_map) best maps based on the optimization metric
    opt_metric_flag : str
        indicates the metric to optimize for, "compact" for polsby popper, "competitiveness" for efficiency gap
    """
    def __init__(self, prefix: str, deviation: float, steps: int, num_maps: int, opt_metric_flag: str):
        # Check prefix
        if prefix not in num_districts:
            raise ValueError(f"Invalid state prefix '{prefix}'")
        self.prefix = prefix

        # Check deviation
        if not (0.001 <= deviation <= 0.1):
            raise ValueError(f"Deviation '{deviation}' out of range. Must be between 0.001 and 0.1.")
        self.deviation = deviation

        # Check steps
        if steps < 0:
            raise ValueError(f"Steps '{steps}' must be >= 0.")
        self.steps = steps

        # Check num_maps
        if not (1 <= num_maps <= 10):
            raise ValueError(f"Number of maps '{num_maps}' out of range. Must be between 1 and 10.")
        self.num_maps = num_maps

        # Check optimization metric
        if opt_metric_flag not in ("compact", "competitiveness"):
            raise ValueError(
                f"Optimization metric '{opt_metric_flag}' is invalid. Must be 'compact' or 'competitiveness'"
            )
        self.opt_metric_flag = opt_metric_flag

        self.state_gdf = self._load_state_gdf()

    # function to get state shapefile
    def _load_state_gdf(self) -> gpd.GeoDataFrame:
        """
        Loads the census block group data for the sate we are generating districts for

        Returns
        -------
        geo_df : GeoDataFrame
            geopandas datagrame of the census block data loaded from the file
        """
        print("\ngetting state GeoDataFrame")
        package_path = os.path.dirname(importlib.util.find_spec("fairymander.generator").origin)
        file_path = os.path.join(package_path, f"Data/finalData/{self.prefix}/{self.prefix}_bg_data.zip")
        geo_df = gpd.read_file(f"zip://{file_path}")
        geo_df.to_crs(epsg=epsg[self.prefix], inplace=True)
        print("Sucessfully loaded state GeoDataFrame")
        return geo_df

    def _get_random_partition(self) -> GeographicPartition:
        """
        Gets an initial random partition of the state to have a starting place for the algorithm

        Returns
        -------
        GeographicPartition
            resulting random partition of the sate
        """
        # get the state's merged shapefile
        state_graph = Graph.from_geodataframe(self.state_gdf)

        simulated_election = updaters.Election(
        "Simulated Election",
        {"Democratic": "party_dem", "Republican": "party_rep"},
        alias = "election"
        )

        partition_updaters = {
            "population": updaters.Tally("C_TOT22"),
            "cut_edges": updaters.cut_edges,
        }

        if self.opt_metric_flag == "compact":
            partition_updaters["polsby-popper"] = polsby_popper
        else:
            partition_updaters["election"] = simulated_election

        return GeographicPartition.from_random_assignment(state_graph, num_districts[self.prefix], self.deviation, 'C_TOT22', updaters=partition_updaters)


    def _generate_maps(self, initial_partition: GeographicPartition) -> list[Tuple[float, list[GeographicPartition]]]:
        """
        Generates district maps based on the initial configuration and a given random starting partition

        Parameters
        ----------
        initial_partition: GeographicPartition
            starting partition for the algorithm to begin running on

        Returns
        -------
        list[Tuple[float, list[GeographicPartition]]]
            list of tuples, where each tuple consists of the optimiation metric for the map,
            and the partition for that map
        """
        # polsby-popper metric
        if self.opt_metric_flag == "compact":
            opt_metric = lambda x: sum(x["polsby-popper"].values())/len(x)
            maximize = True
        # efficiency-gap metric
        else:
            opt_metric = lambda x: abs(x["election"].efficiency_gap())
            maximize = False


        ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)

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
            maximize=maximize,
        )

        best = []
        seen_scores = set()

        for i, item in enumerate(recom_chain.simulated_annealing(
            self.steps,
            recom_chain.jumpcycle_beta_function(200,800),
            beta_magnitude=1,
        )):
            print(f"Finished step {i+1}/{self.steps}", end="\r")

            if self.opt_metric_flag == "compact":
                current_opt_metric = sum(recom_chain.best_part["polsby-popper"].values())/len(recom_chain.best_part)
            else:
                # we apply the negative since heapq uses min heaps
                current_opt_metric = -abs(recom_chain.best_part["election"].efficiency_gap())

            if current_opt_metric not in seen_scores:
                heapq.heappush(best, (current_opt_metric, recom_chain.best_part.assignment))
                if len(best) > self.num_maps:
                    heapq.heappop(best)
            seen_scores.add(current_opt_metric)
        return [(abs(opt_metric), partition) for opt_metric, partition in best]

    def run(self) -> list[gpd.GeoDataFrame]:
        """
        The main runner function for the generator, uses utility in the class to generate district plans
        based on the configuration of the Generator

        Returns
        -------
        final_maps : list[gpd.GeoDataFrame]
            list of geopandas dataframes corresponding to the final generated district maps. they
            are "dissolved", meaning the individual geographic units have been combined into districts
        """
        # polsby-popper metric
        if self.opt_metric_flag == "compact":
            display_metric = "Polsby-Popper"
        # efficiency-gap metric
        else:
            display_metric = "Efficiency-Gap"
        print("getting state partition")
        init_partition=self._get_random_partition()
        print("generating map")
        best = self._generate_maps(init_partition)
        final_maps = []

        # display results
        for opt_metric, partition in best:
            print(f"Map with {display_metric} metric {opt_metric} found: ")
            curr_gdf = self.state_gdf.copy()
            curr_gdf['District'] = curr_gdf.index.map(partition)
            # Group by 'District' and sum the population
            district_population = curr_gdf.groupby('District')['C_TOT22'].sum()

            # Print the population of each district
            print("Population in each district:")
            print(district_population)

            # Visualize the result
            fig, ax = plt.subplots(1, 1, figsize=(10, 10))
            curr_gdf.plot(column='District', ax=ax, legend=True, cmap="rainbow")
            plt.title("District Assignment from Markov Chain ReCom")
            plt.show()

            final_maps.append(curr_gdf)

        # dissolve the maps so they can be returned
        print("Dissolving maps...")
        for index, curr_map in enumerate(final_maps):
            dissolved_gdf = curr_map.dissolve(by='District', aggfunc='sum').drop(columns=['GEOID20'])
            dissolved_gdf['District'] = range(1, len(dissolved_gdf) + 1)
            dissolved_gdf = dissolved_gdf.reset_index(drop=True)
            final_maps[index] = dissolved_gdf
        print("Maps dissolved.")

        return final_maps

    def run_and_save(self, directory: str, file_prefix: str) -> list[gpd.GeoDataFrame]:
        """
        Performs run, returns results and saves the result maps to the specified directory

        Parameters
        ----------
        directory: str
            the directory in the user's filesystem that the maps should be saved under

        file_prefix : str
            the prefix for file names the maps will be saved under

        Returns
        -------
        final_maps : list[gpd.GeoDataFrame]
            list of geopandas dataframes corresponding to the final generated district maps. they
            are "dissolved", meaning the individual geographic units have been combined into districts
        """
        final_maps = self.run()

        print(f"Saving maps to {directory}...")
        for index, curr_map in enumerate(final_maps):
            next_dir = f"{directory}/{file_prefix}/{file_prefix}-{index}"
            if not os.path.exists(next_dir):
                os.makedirs(next_dir)
            curr_map.to_file(f"{next_dir}/{file_prefix}-{index}.shp")
        print("Maps saved.")

        return final_maps
