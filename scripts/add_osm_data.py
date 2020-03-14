import pandas as pd
import pickle
import geopy.distance
import os
from shutil import copyfile

class add_osm_data:

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
        #Count the amenities for each property listing  
        amenity_count = [self.search(lat, lon) for lat, lon in
                         zip(self.df_ads['latitude'], self.df_ads['longitude'])]
        self.amenity_count_df = pd.DataFrame(amenity_count)

    def merge_data(self):
        #Merge as columns to ads data
        self.df_ads_mapdata = pd.concat(
            [self.df_ads.reset_index(drop=True), self.amenity_count_df], axis=1)

