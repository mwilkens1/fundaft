from shapely.geometry.polygon import Polygon
import numpy as np
from shapely.geometry import Point
import pandas as pd
import pickle
import geopy.distance
import os
import json
from shutil import copyfile
from geopy.geocoders import Nominatim
import time

class Add_data:
    """
    This class takes the scraped Daft.ie ads created by Crawl_daft and enriches
    it with:
    - openstreetmap data: counts of amenities (e.g. schools, cafes, etc) in a 
      radius of 0.5 km
    - electoral districts: it checks whether a longitude and latitude is in the 
      polygon defining an electoral district. This allows further on to plot the
      data in a choropleth map.      

    On initialisation, it removes any duplicates that are in the scraped dataset
    and removes any ads that are not within 30 km of Dublin city centre. It 
    tries first to replace the longitude and latitude by geocoding the address.
    If that still fails, the row is removed.

    self.df_ads_mapdata is the final datset

    """

    def __init__(self,df_ads,distance=0.5):
        self.distance = distance
        # Open street map data created with openstreetmap_api.py
        self.osm_data = pickle.load(open("data/osm_data.p", "rb"))
        # Ads crawled with scrape_daft.py
        # Removing any duplicates
        self.df_ads = df_ads.drop_duplicates("ad_id", keep="last").copy()
        self.df_ads_mapdata = pd.DataFrame()

        # Remove coordinates that are not in Dublin
        self.df_ads = self.is_in_dublin(self.df_ads).copy()

        # Try to find better coordinates on the basis of address
        self.geolocate_address()

        # If still no coordinates then remove from data
        temp = self.df_ads.dropna(
            subset=['longitude', 'latitude'], inplace=True)

        if temp is not None:
            self.df_ads.dropna(
                subset=['longitude', 'latitude'], inplace=True).copy()            


    def is_in_dublin(self, df):
        """    
        Test whether coordinates in ad are actually in the Dublin area
        Latitude and longitude are set to NA if this is not the case.
        """
        Dublin = (53.346300, -6.263100)
        searchgrid = self.get_searchgrid(Dublin, distance=30)

        df.loc[df['latitude'] > searchgrid['North'],
                        ['longitude', 'latitude']] = np.nan
        df.loc[df['latitude'] < searchgrid['South'],
                        ['longitude', 'latitude']] = np.nan
        df.loc[df['longitude'] > searchgrid['East'],
                        ['longitude', 'latitude']] = np.nan
        df.loc[df['longitude'] < searchgrid['West'],
                        ['longitude', 'latitude']] = np.nan

        return(df)

    def geolocate_address(self):
        """Returns coordinates on the basis of address"""
        self.geolocator = Nominatim(user_agent="fundaft")

        # If latitude / longitude are missing, try to geocode them on the basis
        # of the address      
        self.coords = [self.get_coords(address) if np.isnan(lat)
                else (lat, lon) for address, lat, lon in
                zip(self.df_ads['property_title'], 
                    self.df_ads['latitude'], 
                    self.df_ads['longitude'])]
        
        df = pd.DataFrame(self.coords, columns=['latitude', 'longitude'])
        
        # If new coordinates are not in Dublin, change to na again
        df = self.is_in_dublin(df)

        self.df_ads[["latitude","longitude"]] = df

    def get_coords(self, address):  
        """Helper function for geolocate_address"""
        while True:
            try:
                location = self.geolocator.geocode(address)                
                break
            except:
                time.sleep(20)

        try:
            latitude = location.latitude
            longitude = location.longitude
        except:
            latitude = np.nan
            longitude = np.nan

        return((latitude, longitude))


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


    def is_closeby(self, lat1, lon1, lat2, lon2, distance=0.5):
        """Test if two locations are 0.5km from each other"""

        distance = geopy.distance.distance((lat1, lon1), (lat2, lon2)).km < distance	        
        
        return(distance)


    def search(self, lat, lon):
        """ Using list comprehensions, count the occurances of each type of amenity
        in a 0.5km radius from each property and returns count of closeby
        amenities in a dictionary """

        # Get the coordinates of the square km around the property
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

        assert len(self.df_ads_mapdata) == len(self.df_ads)

    def recode(self):
        """Some recoding"""
        self.df_ads_mapdata['published_date'] = pd.to_datetime(
            self.df_ads_mapdata.published_date, format='%d/%m/%Y')
        self.df_ads_mapdata['year'] = self.df_ads_mapdata['published_date'].dt.to_period(
            'Y').astype(str)
        self.df_ads_mapdata['month'] = self.df_ads_mapdata['published_date'].dt.to_period(
            'M').astype(str)
        self.df_ads_mapdata['quarter'] = self.df_ads_mapdata['published_date'].dt.to_period(
            'Q').astype(str)


    def add_disctrics(self):
        """Adds electoral districts for creating a plotly choropleth"""

        # File of polygons created with electoral_divisons.py
        districts = pickle.load(open("data/boundaries/ED.p", "rb"))

        def name_area(lon, lat):
            """Testing whether coordinates are in polygon and returning the name of 
            electoral district"""
            
            point = Point(lon, lat)
            area = [point.within(polygon) for polygon in districts.geometry]
            
            return(districts[area].EDNAME.values)

        # Running the function for each point in the data
        temp = [name_area(lon, lat) for (lon, lat) in
                        zip(self.df_ads_mapdata.longitude,
                        self.df_ads_mapdata.latitude)]
                
        assert len(self.df_ads_mapdata) == len(temp)

        self.df_ads_mapdata["EDNAME"] = temp
        
        self.df_ads_mapdata["EDNAME"] = self.df_ads_mapdata["EDNAME"].str[0]


