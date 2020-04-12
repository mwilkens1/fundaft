import geopandas as gpd
import pickle

# Reading file
file = gpd.read_file(
    "data/boundaries/Census2011_Electoral_Divisions_generalised20m.shp")

# Selecting relevant areas
file = file[(file.COUNTY == "02") |
            (file.COUNTY == "03") |
            (file.COUNTY == "04") |
            (file.COUNTY == "05")]

remove_areas = ["Kilsallaghan", "Swords-Glasmore", "Swords-Lissenhall", "Donabate",
                "Lusk", "Rush", "Ballyboghil", "Clonmethan", "Garristown", "Hollywood", "Holmpatrick",
                "Balbriggan Rural", "Balbriggan Urban", "Balscadden", "Skerries"]

file = file[~file['EDNAME'].isin(remove_areas)]

def largest_polygon(i):
    """picks the largest polygon for multipolygon"""
    x = [p.area for p in list(i)]
    return(x.index(max(x)))

# Removing the multipolygons (using only first polygon)
file['geometry'] = [i[largest_polygon(
    i)] if i.geom_type == 'MultiPolygon' else i for i in file.geometry]
file = file.to_crs({'init': 'epsg:4326'}).reset_index()

# pickle to file and to geojson
file.to_file("data/boundaries/ED.geojson", driver="GeoJSON")
pickle.dump(file, open("data/boundaries/ED.p", "wb"))
