from geopy.geocoders import Nominatim

import geopandas as gpd

from shapely.geometry import Point
from shapely.ops import nearest_points

geolocator = Nominatim(user_agent="Rip current")

location = geolocator.geocode("Seaside oregon")
print(location.latitude, location.longitude)

point = Point(location.longitude,location.latitude)

shapefile_path = 'locations/w_10se24.zip'
gdf = gpd.read_file(shapefile_path)

# Find the nearest polygon
nearest_polygon = min(gdf['geometry'], key=lambda polygon: polygon.distance(point))

row = gdf[gdf['geometry'] == nearest_polygon]
print(row,row["WFO"])