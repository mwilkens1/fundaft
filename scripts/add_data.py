from shapely.geometry.polygon import Polygon
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import pickle
import geopy.distance
import os
from shutil import copyfile

class Add_data:
    """
    This class takes the scraped daft.ie ads created by Crawl_daft and enriches
    it with:
    - openstreetmap data: counts of amenities (e.g. schools, cafes, etc) in a 
      radius of 0.5 km
    - electoral districts: it checks whether a longitude and latitude is in the 
      polygon defining an electoral district. This allows further on to plot the
      data in a choropleth map.      

    self.df_ads_mapdata is the final datset

    """

    def __init__(self,osm_data,df_ads,distance=0.5):
        self.distance = distance
        self.osm_data = osm_data
        self.df_ads = df_ads
        self.amenity_count_df = pd.DataFrame()
        self.df_ads_mapdata = pd.DataFrame()

    def get_searchgrid(self, point, distance):
        """Get list with [south latitude, north latitude, west longitude, 
        east longitude] as distance from point """

        d = geopy.distance.distance(distance)

        latitude = []
        longitude = []
        for name, bearing in [('North', 0), ('East', 90), 
                              ('South', 180), ('West', 270)]:

            coordinates = d.destination(point=point, bearing=bearing)
            latitude.append(coordinates.latitude)
            longitude.append(coordinates.longitude)

        searchgrid = dict({'South': min(latitude),
                           'North': max(latitude),
                           'West': min(longitude),
                           'East': max(longitude)})

        return(searchgrid)

    def is_closeby(self, lat1, lon1, lat2, lon2):
        """Test if two locations are 0.5km from each other"""

        distance = geopy.distance.distance((lat1, lon1), (lat2, lon2)).km < 0.5	        
        
        return(distance)

    def search(self, lat, lon):
        """ Using list comprehensions, count the occurances of each type of amenity 
        in a 0.5km radius from each property and returns count of closeby
        amenities in a dictionary """

        #Get the coordinates of the square km around the property
        searchgrid = self.get_searchgrid((lat,lon),distance=self.distance)
        
        counts_dict = {}
        for amenity_type, coordinates in self.osm_data.items():

            #Slice out the square km from the amenity data
            square = coordinates.loc[((coordinates["lat"] > searchgrid['South']) &
                                      (coordinates["lat"] < searchgrid['North']) &
                                      (coordinates["lon"] > searchgrid['West']) &
                                      (coordinates["lon"] < searchgrid['East']))]

            #Within the square km, count those within a 0.5km radius
            count = sum([self.is_closeby(lat1,lon1,lat,lon) for 
                            lat1, lon1 in zip(square['lat'], square['lon'])])

            # Count number of closeby amenities and store into dictionary.
            counts_dict.update({amenity_type: count})

        return(counts_dict)

    def count_amenities(self):
        """Count the amenities for each property listing"""  
        amenity_count = [self.search(lat, lon) for lat, lon in
                         zip(self.df_ads['latitude'], self.df_ads['longitude'])]
        self.amenity_count_df = pd.DataFrame(amenity_count)

    def recode(self):
        """Some recoding"""
        self.df_ads_mapdata['published_date'] = pd.to_datetime(
            self.df_ads_mapdata.published_date)
        self.df_ads_mapdata['year'] = self.df_ads_mapdata['published_date'].dt.to_period(
            'Y').astype(str)
        self.df_ads_mapdata['month'] = self.df_ads_mapdata['published_date'].dt.to_period(
            'M').astype(str)
        self.df_ads_mapdata['quarter'] = self.df_ads_mapdata['published_date'].dt.to_period(
            'Q').astype(str)

    def merge_data(self):
        """Merge as columns to ads data"""
        self.df_ads_mapdata = pd.concat(
            [self.df_ads.reset_index(drop=True), self.amenity_count_df], axis=1)


    def add_disctrics(self):
        """Adds electoral districts for creating a plotly choropleth"""

        # Reading file
        file = gpd.read_file(
            "data/boundaries/Census2011_Electoral_Divisions_generalised20m.shp")

        # Selecting relevant areas
        file = file[(file.COUNTY == "02") |
                    (file.COUNTY == "03") |
                    (file.COUNTY == "04") |
                    (file.COUNTY == "05")]

        remove_areas = ["Kilsallaghan", "Swords-Glasmore", "Swords-Lissenhall", "Donabate",
                        "Lusk", "Rush", "Ballyboghil", "Clonmethan", "Garristown", "Hollywood", "Holmpatrick",
                        "Balbriggan Rural", "Balbriggan Urban", "Balscadden", "Skerries"]

        file = file[~file['EDNAME'].isin(remove_areas)]

        def largest_polygon(i):
            """picks the largest polygon for multipolygon"""
            x = [p.area for p in list(i)]
            return(x.index(max(x)))

        # Removing the multipolygons (using only first polygon)
        file['geometry'] = [i[largest_polygon(
            i)] if i.geom_type == 'MultiPolygon' else i for i in file.geometry]
        file = file.to_crs({'init': 'epsg:4326'}).reset_index()

        # Saving to geojson
        file.to_file("data/boundaries/ED.geojson", driver="GeoJSON")

        def name_area(lon, lat):
            """Testing whether coordinates are in polygon and returning the name of 
            electoral district"""
            point = Point(lon, lat)
            area = [point.within(polygon) for polygon in file.geometry]
            return(file[area].EDNAME.values)

        # Running the function for each point in the data
        self.df_ads_mapdata["EDNAME"] = [name_area(lon, lat) for (lon, lat) in
                                         zip(self.df_ads_mapdata.longitude,
                                             self.df_ads_mapdata.latitude)]
        self.df_ads_mapdata["EDNAME"] = self.df_ads_mapdata["EDNAME"].str[0]
