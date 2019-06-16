# NOTE: cannot be run in Atom; throws an error for the parallel processing
import pandas as pd
import requests
import json
import numpy as np

df_ads = pd.read_pickle('df_ads.pkl')

overpass_url = "https://overpass.kumi.systems/api/interpreter"

def addmapinfo(type,radius=500):

    data = []

    # Build multiple queries in case one query has several types, e.g. pubs and bars
    for i in type:
        data_i = []

        for index, row in df_ads.iterrows():
            lat = row["latitude"]
            lon = row["longitude"]

            overpass_query = """
            [out:json];
            (
            node[""" + i + """](around:""" + str(radius) + """,""" + str(lat) + """,""" + str(lon) + """);
            way[""" + i + """](around:""" + str(radius) + """,""" + str(lat) + """,""" + str(lon) + """);
            relation[""" + i + """](around:""" + str(radius) + """,""" + str(lat) + """,""" + str(lon) + """);
            );
            out center;
            """
            response = requests.get(overpass_url, params={'data': overpass_query})
            response_json = response.json()

            data_i.append(len(response_json['elements']))

        data = list(np.sum([data,data_i],axis=0))

    return(data)

type_dict = {"pubs": ['"amenity"="pub"','"amenity"="bar"'], "caferestaurants": ['"amenity"="restaurant"','"amenity"="cafe"'], 'schools': ['"amenity"="school"'], 'stations': ['"railway"="platform"'], "platforms": ['"public_transport"="platform"'],'parks': ['"leisure"="park"'], 'churches': ['"amenity"="place_of_worship"'], 'health': ['"amenity"="clinic"','"amenity"="doctor"'], 'sports': ['"leisure"="pitch"','"leisure"="fitness_centre"','"leisure"="sports_centre"'], 'shops': ['"shop"']}

#df_mapdata = pd.DataFrame()

#for key,value in type_dict.items():

#    data = addmapinfo(type=value)

#    df_mapdata = pd.concat([df_mapdata,pd.DataFrame({key: data})], axis=1)

#df_ads_mapdata.to_pickle('df_ads_mapdata.pkl')    


# Parallel processing with a worker per variable
from multiprocessing import Pool

# worker function
def worker(value):
    data = addmapinfo(type=value)
    return data

# overall job
if __name__ == '__main__':

    p = Pool()
    data = p.map(worker, [value for key, value in type_dict.items()])

    df_mapdata = pd.DataFrame()

    i = 0
    for key,value in type_dict.items():
        df_mapdata = pd.concat([df_mapdata,pd.DataFrame({key: data[i]})], axis=1)
        i += 1

    df_ads_mapdata = pd.concat([df_ads,df_mapdata], axis=1)

    df_ads_mapdata.to_pickle('df_ads_mapdata.pkl')

    p.close()
