import pandas as pd
import requests
import geopy.distance
import pickle

overpass_url = "https://overpass.kumi.systems/api/interpreter"

# Get list of lists of amenities in 30km around the centre of Dublin

type_dict = {"pubs": ['"amenity"="pub"','"amenity"="bar"'], "caferestaurants": ['"amenity"="restaurant"','"amenity"="cafe"'], 'schools': ['"amenity"="school"'], 'stations': ['"railway"="platform"'], "platforms": ['"public_transport"="platform"'],'parks': ['"leisure"="park"'], 'churches': ['"amenity"="place_of_worship"'], 'health': ['"amenity"="clinic"','"amenity"="doctor"'], 'sports': ['"leisure"="pitch"','"leisure"="fitness_centre"','"leisure"="sports_centre"'], 'shops': ['"shop"']}

osm_data = {}

for key, value in type_dict.items():

    string = ""
    for i in value:

        string = string + """   node[""" + str(i).replace("'","") + """](around:30000,53.346300,-6.263100);
        way[""" + str(i).replace("'","") + """](around:30000,53.346300,-6.263100);
        relation[""" + str(i).replace("'","") + """](around:30000,53.346300,-6.263100);
        """

    overpass_query = """
    [out:json];
    (
    """ + string + """
    );
    out center;
    """

    response = requests.get(overpass_url, params={'data': overpass_query})

    assert response.status_code == 200

    response_json = response.json()

    dict_key = {}

    for k in ["id","lat","lon"]:

        x = []
        for e in response_json["elements"]:

            if k in e:
                x.append(e[k])
            else:
                if k in e["center"]:
                    x.append(e["center"][k])

        dict_key.update({k:x})

        df_key = pd.DataFrame(dict_key)

    osm_data.update({key:df_key})

pickle.dump(osm_data, open("osm_data.p", "wb"))