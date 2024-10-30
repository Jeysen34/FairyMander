import geopandas as gpd
import folium
import branca.colormap as cm
from fairymander.data import folium_longlat
from folium import plugins

"""
This module contains utilities to convert pandas dataframes into interactive maps
using folium
"""

def map_to_folium(state: str, district_gdf: gpd.GeoDataFrame) -> folium.Map:
    """
    Converts the given geopandas dataframe district map into an interactable visualization in folium

    Parameters
    ----------
    state: str
        the two letter abbreviation for the state the district map belongs to (i,e, az, fl, ny)
    district_gdf: GeoDataFrame
        dataframe containing the districting plan to be viusalized for the given state

    Returns
    -------
    districtMap: Map
        folium map containing the visualization for the district map
    """
    lat, long, zoom = folium_longlat[state]
    # use folium.map to create a map and center it using latitude and longitude coordinates
    district_map = folium.Map(location=[lat, long], zoom_start=zoom) # (arizona)

    # create colormap to display on the map
    minDis = district_gdf["District"].min()
    maxDis = district_gdf["District"].max()
    colormap = cm.LinearColormap(
        colors=[
                '#2729de','#a28b9a','#c09343','#3eb62c','#7cc8f8','#4A5C64','#4b9276','#d96bab','#F9A78F','#b26e13',
                '#001bff','#99A8AF','#016b2d','#f2fa20','#9376bb','#16d61e','#c23ba8','#00f3ff','#1169ec','#d40cc8',
                '#d9a892','#22d624','#cdcbdf','#6c862a','#960c88','#d91830','#f41563','#434099','#33eb02','#f49eaf',
                '#8b492a','#8a6de4','#9bbb2d','#12e440','#8f965f','#77c644','#451d1e','#9761e1','#3d24e5','#346b07',
                '#e8a6a3','#621b43','#ff5900','#338b03','#0a1c1f','#f36440','#d0f5a0','#cc0bdd','#b47a97','#F3801B',
                '#b6354a','#a5a3df'
                ],
        vmin=minDis,
        vmax=maxDis,
        caption='District'
    )

    # add a caption to the colormap
    colormap.caption = "District"

    # option to fullscreen
    plugins.Fullscreen(
        position='topleft',
        title='Expand',
        title_cancel='Exit',
    ).add_to(district_map)

    # create a style function for the map that fills in each district with a color based on each district, starting from district 1 up to all districts in that state
    def style_function(feature):
        colorDist = colormap(feature['properties']['District'])
        return {
            "color": 'black',
            "weight": 1,
            "fillOpacity": 0.5,
            "fillColor": colorDist,
        }

    # show details when hovering over a district on the map
    tooltip = folium.GeoJsonTooltip(
        fields=["District", "C_TOT22"],
        aliases=["District:", "Population:"],
        labels=True,
        style="""
            border-radius: 10%/50%;
            border: 2px solid red;
            color: blue;
    """
    )

    # use folium to display district boundaries on the map
    folium.GeoJson(
        district_gdf,
        style_function=style_function,
        tooltip=tooltip,
    ).add_to(district_map)

    # add the colormap to the map
    colormap.add_to(district_map)

    return district_map

def map_to_folium_from_file(state: str, file_path: str) -> gpd.GeoDataFrame:
    """
    Converts a geopandas dataframe district map pulled from the given file path
    into an interactable visualization in folium

    Parameters
    ----------
    state: str
        the two letter abbreviation for the state the district map belongs to (i,e, az, fl, ny)

    file_path: str
        the .shp file path for the geodataframe to load

    Returns
    -------
    districtMap: Map
        folium map containing the visualization for the district map
    """
    return map_to_folium(state, gpd.read_file(file_path))
