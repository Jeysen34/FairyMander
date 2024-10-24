# Import the folium library
import folium

# Create a map centered around Arizona
map_arizona = folium.Map(location=[34.4484, -112.0740], zoom_start=6)

# Add a marker at a specific location
folium.Marker(
    location=[33.4484, -112.0740], 
    icon=folium.Icon(color="red"), 
    popup='Arizona').add_to(map_arizona)

# Save the map as an HTML file
map_arizona.save('arizona_map.html')
