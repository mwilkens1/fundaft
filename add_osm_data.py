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

def loop_over_ads(lat, lon):
    """ Using list comprehensions, count the occurances of each type of amenity 
    in a 0.5 mile radius from each property and returns count of closeby
    amenities in a dictionary """

    searchgrid = get_searchgrid((lat,lon),distance=0.5)

    # Count number of closeby amenities and store into dictionary.
    counts_dict = {}
    for amenity_type, coordinates in osm_data.items():

        slice = coordinates.loc[((coordinates["lat"] > searchgrid['South']) &
                                 (coordinates["lat"] < searchgrid['North']) &
                                 (coordinates["lon"] > searchgrid['West']) &
                                 (coordinates["lon"] < searchgrid['East']))]
        counts_dict.update({amenity_type: len(slice)})

    return(counts_dict)


#Run the function
amenity_count = [loop_over_ads(lat, lon) for lat, lon in
                 zip(df_ads['latitude'], df_ads['longitude'])]
amenity_count_df = pd.DataFrame(amenity_count)

#Merge as columns to ads data
df_ads_mapdata = pd.concat(
    [df_ads.reset_index(drop=True), amenity_count_df], axis=1)

#Update the file
os.rename('df_ads_mapdata.pkl', 'df_ads_mapdata_old.pkl')
df_ads_mapdata.to_pickle('df_ads_mapdata.pkl')
