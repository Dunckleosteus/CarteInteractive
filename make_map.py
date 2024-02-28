import folium

# Create a map object
m = folium.Map(location=[51.5074, -0.1278], zoom_start=10)

# Add markers or other features to the map
folium.Marker(location=[51.5074, -0.1278], popup='London').add_to(m)
folium.Marker(location=[48.8566, 2.3522], popup='Paris').add_to(m)

# Save the map as an HTML file
m.save('map.html')
