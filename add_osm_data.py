import pandas as pd
import pickle
import geopy.distance
import os
from shutil import copyfile

#Uses df_ads, the scraped data from daft.ie 
df_ads = pd.read_pickle('df_ads.pkl')

#And osm_data, the data from openstreetmaps
osm_data = pickle.load(open("osm_data.p", "rb"))

#Combines the two
def loop_over_ads(lat,lon): 
    """ Using list comprehensions, count the occurances of each type of amenity 
    in a 0.5 mile radius from each property and returns count of closeby
    amenities in a dictionary """

    def test_closeby(x, y):
        """Select amenities 0.5 km of property"""
        is_closeby = geopy.distance.distance((x,y),(lat,lon)).km < 0.5
        return(is_closeby)

    # Count number of closeby amenities and store into dictionary.
    counts_dict = {}
    for amenity_type, coordinates in osm_data.items():

        count = sum([test_closeby(x, y)
                     for x, y in zip(coordinates['lat'], coordinates['lon'])])
        counts_dict.update({amenity_type: count})

    return(counts_dict)

#Run the function
amenity_count = [loop_over_ads(lat, lon) for lat, lon in 
                 zip(df_ads['latitude'],df_ads['longitude'])]
amenity_count_df = pd.DataFrame(amenity_count)

#Merge as columns to ads data
df_ads_mapdata = pd.concat(
    [df_ads.reset_index(drop=True), amenity_count_df], axis=1)

#Update the file
os.rename('df_ads_mapdata.pkl', 'df_ads_mapdata_old.pkl')
df_ads_mapdata.to_pickle('df_ads_mapdata.pkl')
