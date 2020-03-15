from scripts.scrape_daft import Crawl_daft, Daft_spider
from scripts.add_data import Add_data
import pickle
import pandas as pd

# Initiate crawler
crawler = Crawl_daft()

# County days since the last crawl and create the url
crawler.count_days_since_last_crawl()
crawler.create_url()

# Crawl
crawler.crawl()

#import openstreetmap_api
osm_data = pickle.load(open("data/osm_data.p", "rb"))

#Initalise add_osm_data class
add_data = Add_data(osm_data, crawler.data)
add_data.count_amenities()
add_data.merge_data()

#add electoral districts
add_data.add_disctrics()

#recodes
add_data.recode()

df_ads_mapdata_old = pd.read_pickle('data/df_ads_mapdata.pkl')

len(df_ads_mapdata_old)
len(add_data.df_ads_mapdata)

df_ads_mapdata = df_ads_mapdata_old.append(
    add_data.df_ads_mapdata, ignore_index=True, sort=True)

df_ads_mapdata = df_ads_mapdata.drop_duplicates()

len(df_ads_mapdata)

#Saves to file
df_ads_mapdata.to_pickle('data/df_ads_mapdata.pkl')