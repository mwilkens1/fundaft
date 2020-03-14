from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
import numpy as np

def data_for_map(df_ads_mapdata):
    """Saves to file the a dataset and a geojson for creating a plotly choropleth"""

    # Reading file 
    file = gpd.read_file(
        "data/boundaries/Census2011_Electoral_Divisions_generalised20m.shp")

    # Selecting relevant areas
    file = file[(file.COUNTY == "02") |
                (file.COUNTY == "03") |
                (file.COUNTY == "04") |
                (file.COUNTY == "05")]

    remove_areas = ["Kilsallaghan","Swords-Glasmore","Swords-Lissenhall","Donabate",
    "Lusk","Rush","Ballyboghil","Clonmethan","Garristown","Hollywood","Holmpatrick",
    "Balbriggan Rural","Balbriggan Urban","Balscadden","Skerries"]

    file = file[~file['EDNAME'].isin(remove_areas)]

    def largest_polygon(i):
        """picks the largest polygon for multipolygon"""
        x = [p.area for p in list(i)]
        return(x.index(max(x)))

    # Removing the multipolygons (using only first polygon)
    file['geometry'] = [i[largest_polygon(i)] if i.geom_type == 'MultiPolygon' else i for i in file.geometry]
    file = file.to_crs({'init': 'epsg:4326'}).reset_index()

    # Saving to geojson
    file.to_file("data/boundaries/ED.geojson", driver="GeoJSON")       

    # Loading ads data
    #df_ads_mapdata = pd.read_pickle('data/df_ads_mapdata.pkl')

    def name_area(lon, lat):
        """Testing whether coordinates are in polygon and returning the name of 
        electoral district"""
        point = Point(lon, lat)
        area = [point.within(polygon) for polygon in file.geometry]
        return(file[area].EDNAME.values)

    # Running the function for each point in the data
    df_ads_mapdata["EDNAME"] = [name_area(lon, lat) for (lon, lat) in
                                zip(df_ads_mapdata.longitude, 
                                    df_ads_mapdata.latitude)]
    df_ads_mapdata["EDNAME"] = df_ads_mapdata["EDNAME"].str[0]

    df = df_ads_mapdata.groupby("EDNAME")[['price']].median().reset_index()
    df["logprice"] = np.log(df.price)
    df["price"] = round(df.price,-3)

    df.to_pickle('data/data_for_mapplot.pkl')
