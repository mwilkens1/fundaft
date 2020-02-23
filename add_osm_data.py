import pandas as pd
import pickle
import geopy.distance
import os

# Using list comprehensions, count the occurances of each type of amenity in a 0.5 mile radius from each property
df_ads = pd.read_pickle('df_ads.pkl')
osm_data = pickle.load(open("osm_data.p", "rb"))

def loop_over_ads(lat,lon):

    def func(x, y):
        out = geopy.distance.distance((x,y),(lat,lon)).km < 0.5
        return(out)

    dict_loop = {}
    for key, value in osm_data.items():

        z = sum([func(x, y) for x, y in zip(value['lat'], value['lon'])])
        dict_loop.update({key: z})

    return(dict_loop)

result = pd.DataFrame([loop_over_ads(lat,lon) for lat, lon in zip(df_ads['latitude'],df_ads['longitude'])])

df_ads_mapdata = pd.concat([df_ads.reset_index(drop=True),result],axis=1)

os.rename('df_ads_mapdata.pkl', 'df_ads_mapdata_old.pkl')
df_ads_mapdata.to_pickle('df_ads_mapdata.pkl')
