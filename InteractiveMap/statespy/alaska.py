# Import the folium library
import folium

# Create a map centered around Alaska
map_alaska = folium.Map(location=[63.5888, -154.4931], zoom_start=4)

# Add a marker at a specific location
folium.Marker(
    location=[63.5888, -154.4931], 
    icon=folium.Icon(color="red"), 
    popup='Alaska').add_to(map_alaska)

# Save the map as an HTML file
map_alaska.save('alaska_map.html')