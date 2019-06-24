import pandas as pd
import requests

df_ads = pd.read_pickle('df_ads.pkl')

overpass_url = "https://overpass.kumi.systems/api/interpreter"

def addmapinfo(dict,radius=500, tries=5):

    df = []

    # Performing the query to the API for each row of data
    for index, row in df_ads.iterrows():

        data = []

        lat = row["latitude"]
        lon = row["longitude"]

        # Compiling the query to the API to account for multiple queries (e.g. pubs and bars at the same time)
        string = ""
        for i in dict.values():

            for j in i:

                string = string + """   node[""" + str(j).replace("'","") + """](around:""" + str(radius) + """,""" + str(lat) + """,""" + str(lon) + """);
                way[""" + str(j).replace("'","") + """](around:""" + str(radius) + """,""" + str(lat) + """,""" + str(lon) + """);
                relation[""" + str(j).replace("'","") + """](around:""" + str(radius) + """,""" + str(lat) + """,""" + str(lon) + """);
                """

        overpass_query = """
        [out:json];
        (
        """ + string + """
        );
        out center;
        """

        # Server seems to time out or refuse randomly.
        for n in range(tries):

            try:

                response = requests.get(overpass_url, params={'data': overpass_query})

            except:

                print("Exception occured for row " + str(index) + ", ad_id " + row.ad_id)
                response = None
                continue

            else:

                break

        if response == None:

            continue

        # if the html response is not 200, go to the next row in the data
        if response.status_code != 200:

            print("Response code " + str(response.status_code) + " for row " + str(index) + ", ad_id " + row.ad_id)
            continue

        response_json = response.json()

        # Counting the occurances of any of the values of a particular key
        for key, value in dict.items():

            count = 0

            l = []

            for j in value:

                j = j.replace('"',"'").replace("=",": ")
                l.append(j)

            for e in response_json["elements"]:

                if any(x in str(e["tags"]) for x in l):

                    count += 1

            data.append(count)

        df.append(data)

    df = pd.DataFrame(df, columns = dict.keys())

    return(df)


type_dict = {"pubs": ['"amenity"="pub"','"amenity"="bar"'], "caferestaurants": ['"amenity"="restaurant"','"amenity"="cafe"'], 'schools': ['"amenity"="school"'], 'stations': ['"railway"="platform"'], "platforms": ['"public_transport"="platform"'],'parks': ['"leisure"="park"'], 'churches': ['"amenity"="place_of_worship"'], 'health': ['"amenity"="clinic"','"amenity"="doctor"'], 'sports': ['"leisure"="pitch"','"leisure"="fitness_centre"','"leisure"="sports_centre"'], 'shops': ['"shop"']}

df_mapdata = addmapinfo(dict=type_dict)

df_ads_mapdata = pd.concat([df_ads,df_mapdata], axis=1)

df_ads_mapdata.to_pickle('df_ads_mapdata.pkl')
