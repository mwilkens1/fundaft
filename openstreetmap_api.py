import pandas as pd
import requests
import geopy.distance
import pickle

#This module gets a list of amenities in 30km around the centre of Dublin.
#Using the openstreetmap API
overpass_url = "https://overpass.kumi.systems/api/interpreter"

# Get list of lists of amenities in 30km around the centre of Dublin
# Here the types of amenities are specified according to openstreetmap 
# conventions. Some are merged into one category.
type_dict = {"pubs": ['"amenity"="pub"','"amenity"="bar"'], 
             "caferestaurants": ['"amenity"="restaurant"','"amenity"="cafe"'], 
             'schools': ['"amenity"="school"'], 
             'stations': ['"railway"="platform"'], 
             "platforms": ['"public_transport"="platform"'],
             'parks': ['"leisure"="park"'], 
             'churches': ['"amenity"="place_of_worship"'], 
             'health': ['"amenity"="clinic"','"amenity"="doctor"'], 
             'sports': ['"leisure"="pitch"',
                        '"leisure"="fitness_centre"',
                        '"leisure"="sports_centre"'], 
             'shops': ['"shop"']}

osm_data = {}

for type_name, type_definition in type_dict.items():

    #Creating the query for each amenity type 
    type_query = ""
    #Pasting different queries for subtypes together
    for subtype in type_definition:

        type_query = type_query + \
                     """   node[""" + \
                     str(subtype).replace("'","") + \
                     """](around:30000,53.346300,-6.263100);
                     way[""" + \
                     str(subtype).replace("'","") + \
                     """](around:30000,53.346300,-6.263100);
                     relation[""" + \
                     str(subtype).replace("'", "") + \
                     """](around:30000,53.346300,-6.263100);"""

    # Building the query
    overpass_query = """
    [out:json];
    (
    """ + type_query + """
    );
    out center;
    """
    
    #querying the database
    response = requests.get(overpass_url, params={'data': overpass_query})

    #Checking the response
    assert response.status_code == 200

    #Converting to json
    response_json = response.json()

    #Building a dictionary with the results
    type_results = {}

    #Extract the id of the amenity and its coordinates
    for var in ["id","lat","lon"]:

        values = []
        #for each element in the json
        for element in response_json["elements"]:

            #test if id, latitude or longitude is there and add to data
            if var in element:
                values.append(element[var])
            else:
                if var in element["center"]:
                    values.append(element["center"][var])

        type_results.update({var: values})

        #Create dataframe of id, longitude, latitude for subcategory    
        df_type_results = pd.DataFrame(type_results)

    #Add each type as a dataframe to the list of dataframes
    osm_data.update({type_name: df_type_results})

pickle.dump(osm_data, open("osm_data.p", "wb"))
