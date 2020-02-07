import pandas as pd
import os

os.remove('df_ads_mapdata_old.pkl')
os.rename('df_ads_mapdata.pkl', 'df_ads_mapdata_old.pkl')

df_ads_mapdata_old = pd.read_pickle('df_ads_mapdata_old.pkl')

df_ads_mapdata_new = pd.read_pickle('df_ads_mapdata.pkl')

len(df_ads_mapdata_old)
len(df_ads_mapdata_new)

df_ads_mapdata = df_ads_mapdata_old.append(df_ads_mapdata_new, ignore_index=True, sort=True)

assert len(df_ads_mapdata) == len(df_ads_mapdata_old) + len(df_ads_mapdata_new)

df_ads_mapdata = df_ads_mapdata.drop_duplicates()

len(df_ads_mapdata)

df_ads_mapdata.to_pickle('df_ads_mapdata.pkl')
