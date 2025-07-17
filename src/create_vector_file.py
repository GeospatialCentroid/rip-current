import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def csv_to_point_vector(df, lat_col, lng_col, output_file):
    """
    Converts a CSV file with lat/lng columns into a spatial file
    (Shapefile, GeoPackage, GeoJSON, or KML).

    Parameters:
    - df (dataframe): the dateframe.
    - lat_col (str): Name of the latitude column.
    - lng_col (str): Name of the longitude column.
    - output_file (str): Output file name (.shp, .gpkg, .geojson, .kml)
    """

    print("the dateframe is", df)

    # Validate columns
    if lat_col not in df.columns or lng_col not in df.columns:
        raise ValueError(f"Columns '{lat_col}' and/or '{lng_col}' not found in CSV.")

    # Create geometry
    geometry = [Point(xy) for xy in zip(df[lng_col], df[lat_col])]

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    gdf.set_crs(epsg=4326, inplace=True)  # WGS84

    # Determine driver
    ext = output_file.lower().split('.')[-1]

    if ext == 'shp':
        driver = 'ESRI Shapefile'
    elif ext == 'gpkg':
        driver = 'GPKG'
    elif ext == 'geojson':
        driver = 'GeoJSON'
    elif ext == 'kml':
        driver = 'KML'
        # KML requires only one geometry column named 'Name' or 'description' sometimes
        # but GeoPandas handles this automatically if using `to_file`
    else:
        raise ValueError("Unsupported file type. Use '.shp', '.gpkg', '.geojson', or '.kml'.")

    # Export
    gdf.to_file(output_file, driver=driver)
    print(f"Exported {len(gdf)} points to '{output_file}' as {driver}.")

