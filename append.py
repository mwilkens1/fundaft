import pandas as pd

df_ads_old = pd.read_pickle('df_ads_0201.pkl')

df_ads_new = pd.read_pickle('df_ads.pkl')

len(df_ads_old)
len(df_ads_new)

df_ads = df_ads_old.append(df_ads_new, ignore_index=True, sort=True)

assert len(df_ads) == len(df_ads_old) + len(df_ads_new)

df_ads = df_ads.drop_duplicates()

len(df_ads)

df_ads.to_pickle('df_ads.pkl')
