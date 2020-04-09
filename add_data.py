from shapely.geometry.polygon import Polygon
import numpy as np
from shapely.geometry import Point
import pandas as pd
import pickle
import geopy.distance
import os
import json
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

    def __init__(self,df_ads,distance=0.5):
        self.distance = distance
        # Open street map data created with openstreetmap_api.py
        self.osm_data = pickle.load(open("data/osm_data.p", "rb"))
        # Ads crawled with scrape_daft.py
        self.df_ads = df_ads
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

    def add_amenities(self):
        """Count the amenities for each property listing and 
        merge this to the scraped ads file"""  
        amenity_count = [self.search(lat, lon) for lat, lon in
                         zip(self.df_ads['latitude'], self.df_ads['longitude'])]
        
        self.df_ads_mapdata = pd.concat(
            [self.df_ads.reset_index(drop=True), pd.DataFrame(amenity_count)], axis=1)

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
        


    def add_disctrics(self):
        """Adds electoral districts for creating a plotly choropleth"""

        # File of polygons created with electoral_divisons.py
        with open("data/boundaries/ED.geojson", 'r') as f:
            districts = json.load(f)

        def name_area(lon, lat):
            """Testing whether coordinates are in polygon and returning the name of 
            electoral district"""
            
            point = Point(lon, lat)
            area = [point.within(polygon) for polygon in districts.geometry]
            
            return(districts[area].EDNAME.values)

        # Running the function for each point in the data
        self.df_ads_mapdata["EDNAME"] = [name_area(lon, lat) for (lon, lat) in
                                         zip(self.df_ads_mapdata.longitude,
                                             self.df_ads_mapdata.latitude)]
        
        self.df_ads_mapdata["EDNAME"] = self.df_ads_mapdata["EDNAME"].str[0]
