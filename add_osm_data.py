import pandas as pd
import pickle
import geopy.distance
import os
from shutil import copyfile

#Uses df_ads, the scraped data from daft.ie 
df_ads = pd.read_pickle('df_ads.pkl')

#And osm_data, the data from openstreetmaps
osm_data = pickle.load(open("osm_data.p", "rb"))

def get_searchgrid(point, distance):
    """Get list with [south latitude, north latitude, west longitude, 
    east longitude] as distance from point """

    d = geopy.distance.distance(distance)

    latitude = []
    longitude = []
    for name, bearing in [('North', 0), ('East', 90), ('South', 180), ('West', 270)]:

        coordinates = d.destination(point=point, bearing=bearing)
        latitude.append(coordinates.latitude)
        longitude.append(coordinates.longitude)

    searchgrid = dict({'South': min(latitude),
                       'North': max(latitude),
                       'West': min(longitude),
                       'East': max(longitude)})

    return(searchgrid)

def is_closeby(lat1, lon1, lat2, lon2):
    """Test if two locations are 0.5km from each other"""

    distance = geopy.distance.distance((lat1, lon1), (lat2, lon2)).km < 0.5	        
    return(distance)

def count_amenities(lat, lon):
    """ Using list comprehensions, count the occurances of each type of amenity 
    in a 0.5km radius from each property and returns count of closeby
    amenities in a dictionary """

    #Get the coordinates of the square km around the property
    searchgrid = get_searchgrid((lat,lon),distance=0.5)
    
    counts_dict = {}
    for amenity_type, coordinates in osm_data.items():

        #Slice out the square km from the amenity data
        square = coordinates.loc[((coordinates["lat"] > searchgrid['South']) &
                                  (coordinates["lat"] < searchgrid['North']) &
                                  (coordinates["lon"] > searchgrid['West']) &
                                  (coordinates["lon"] < searchgrid['East']))]

        #Within the square km, count those within a 0.5km radius
        count = sum([is_closeby(lat1,lon1,lat,lon) for 
                        lat1, lon1 in zip(square['lat'], square['lon'])])

        # Count number of closeby amenities and store into dictionary.
        counts_dict.update({amenity_type: count})

    return(counts_dict)

#Count the amenities for each property listing
amenity_count = [count_amenities(lat, lon) for lat, lon in
                 zip(df_ads['latitude'], df_ads['longitude'])]
amenity_count_df = pd.DataFrame(amenity_count)

#Merge as columns to ads data
df_ads_mapdata = pd.concat(
    [df_ads.reset_index(drop=True), amenity_count_df], axis=1)

#Update the file
os.rename('df_ads_mapdata.pkl', 'df_ads_mapdata_old.pkl')
df_ads_mapdata.to_pickle('df_ads_mapdata.pkl')