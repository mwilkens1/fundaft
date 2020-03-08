from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
import plotly.express as px
import json

# Reading file 
file = gpd.read_file(
    "boundaries/Census2011_Electoral_Divisions_generalised20m.shp")

# Selecting relevant areas
file = file[(file.COUNTY == "02") |
            (file.COUNTY == "03") |
            (file.COUNTY == "04") |
            (file.COUNTY == "05")]

remove_areas = ["Kilsallaghan","Swords-Glasmore","Swords-Lissenhall","Donabate",
"Lusk","Rush","Ballyboghil","Clonmethan","Garristown","Hollywood","Holmpatrick",
"Balbriggan Rural","Balbriggan Urban","Balscadden","Skerries"]

file = file[~file['EDNAME'].isin(remove_areas)]

def largest_polygon(i):
    """picks the largest polygon for multipolygon"""
    x = [p.area for p in list(i)]
    return(x.index(max(x)))

# Removing the multipolygons (using only first polygon)
file['geometry'] = [i[largest_polygon(i)] if i.geom_type == 'MultiPolygon' else i for i in file.geometry]
file = file.to_crs({'init': 'epsg:4326'}).reset_index()

# Saving to geojson
file.to_file("boundaries/ED.geojson", driver="GeoJSON")

# Opening geojson
with open("boundaries/ED.geojson") as json_file:
    areas = json.load(json_file)

# Loading ads data
df_ads_mapdata = pd.read_pickle('df_ads_mapdata.pkl')

def name_area(lon, lat):
    """Testing whether coordinates are in polygon and returning the name of 
    electoral district"""
    point = Point(lon, lat)
    area = [point.within(polygon) for polygon in file.geometry]
    return(file[area].EDNAME.values)

# Running the function for each point in the data
df_ads_mapdata["EDNAME"] = [name_area(lon, lat) for (lon, lat) in
                            zip(df_ads_mapdata.longitude, df_ads_mapdata.latitude)]
df_ads_mapdata["EDNAME"] = df_ads_mapdata["EDNAME"].str[0]

df = df_ads_mapdata.groupby("EDNAME")[['price']].median().reset_index()

fig = px.choropleth_mapbox(df, geojson=areas, color="price",
                           locations="EDNAME", featureidkey="properties.EDNAME",
                           center={"lat": 53.32, "lon": -6.3},
                           mapbox_style="carto-positron", zoom=10,
                           opacity=0.6,
                           labels={'EDNAME': '', 'price': "Median price"},
                           title="Median price on Daft.ie",
                           hover_name="EDNAME",
                           width=1000, height=1000)
fig.show()


