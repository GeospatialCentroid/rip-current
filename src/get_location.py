from geopy.geocoders import Nominatim

import geopandas as gpd

from shapely.geometry import Point
from shapely.ops import nearest_points

import urllib.request
import time
import json
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document"
}

def get_location(location_name):

    print("searching for the location of: ",location_name)

    geolocator = Nominatim(user_agent="Rip current")

    location = geolocator.geocode(location_name)
    if location:

        row = get_closest_WFO(location.longitude, location.latitude)
        return {"geo":row,"lat":location.latitude,"lng":location.longitude}
    else:
        return

def get_location_google(location_name,key):
    # create a url which has the lat and lng
    print("searching for "+location_name)
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(str(location_name), key)
    result = get_url_result(url)

    if result and len(result["results"])>0:
        # print(result)
        lat = result["results"][0]['geometry']['location']['lat']
        lng= result["results"][0]['geometry']['location']['lng']
        row, distance = get_closest_WFO(lat,lng)
        return {"WFO":str(row["WFO"]),"distance_from_wfo":distance,"lat":lat,"lng":lng}
    else:
        print("Error: ",result)
        return

def get_closest_WFO(lat,lng):
    point = Point(lng, lat)
    shapefile_path = 'locations/w_10se24.zip'
    gdf = gpd.read_file(shapefile_path).to_crs("epsg:4326")
    # Calculate distances and find the closest geometry
    gdf['distance'] = gdf['geometry'].distance(point)
    closest_row = gdf.loc[gdf['distance'].idxmin()]

    return closest_row, closest_row['distance']

def get_url_result(url):
    attempt = 0
    print("get_url_result:",url )
    try:
        response = requests.get(url, headers=headers)

        return response.json()


    except Exception as err:

        if attempt > 1:
            print("More than 3 attempts failed to retrieve file. Aborting.")
            return
        else:
            print("Retrieving file failed, waiting 5 sec")
            print("Message was:", str(err))
            time.sleep(1)

    finally:
        attempt += 1