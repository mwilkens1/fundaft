from scripts.scrape_daft import Crawl_daft, Daft_spider
from scripts.add_osm_data import add_osm_data
from scripts.map import data_for_map
import pickle
import pandas as pd

# Initiate crawler
crawler = Crawl_daft()

# County days since the last crawl and create the url
crawler.count_days_since_last_crawl()
crawler.create_url()

# Create backup of data
#crawler.backup()

# Crawl
crawler.crawl()

#Save to pickle
#crawler.data.to_pickle('data/df_ads.pkl')

#import openstreetmap_api
osm_data = pickle.load(open("data/osm_data.p", "rb"))

#Initalise add_osm_data class
add_osm_data = add_osm_data(osm_data, crawler.data)
add_osm_data.count_amenities()
add_osm_data.merge_data()

df_ads_mapdata_old = pd.read_pickle('data/df_ads_mapdata.pkl')

len(df_ads_mapdata_old)
len(add_osm_data.df_ads_mapdata)

df_ads_mapdata = df_ads_mapdata_old.append(
    add_osm_data.df_ads_mapdata, ignore_index=True, sort=True)

df_ads_mapdata = df_ads_mapdata.drop_duplicates()

len(df_ads_mapdata)

#Saves to file
df_ads_mapdata.to_pickle('data/df_ads_mapdata.pkl')

#Creates two files to make the choropleth map with plotly
data_for_map(df_ads_mapdata)
