from scrape_daft import Crawl_daft, Daft_spider
from add_data import Add_data
import pickle
import pandas as pd

# Initiate crawler
crawler = Crawl_daft()

# County days since the last crawl and create the url
crawler.create_url()

# Crawl
crawler.crawl()

# Initalise add_data class
add_data = Add_data(crawler.data)

# adding counts of open street data amenities
add_data.add_amenities()

# add electoral districts
add_data.add_disctrics()

#recodes
add_data.recode()

# Read data scraped so far
df_ads_mapdata_old = pd.read_csv('data/df_ads_mapdata.csv')

len(df_ads_mapdata_old)
len(add_data.df_ads_mapdata)

# Appending file to the data scraped so far
df_ads_mapdata = df_ads_mapdata_old.append(
    add_data.df_ads_mapdata, ignore_index=True, sort=True)

# Removing any duplicates
# Some duplicates arise because an ad has been updated. We keep the last.
df_ads_mapdata = df_ads_mapdata.drop_duplicates("ad_id", keep="last")

len(df_ads_mapdata)

# Saves to file
df_ads_mapdata.to_csv('data/df_ads_mapdata.csv', index=False) 


