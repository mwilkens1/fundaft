import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

df_ads_mapdata = pd.read_pickle('df_ads_mapdata.pkl')

# Plotting mean price per property type and number of bedrooms

props = df_ads_mapdata.property_type.value_counts()[0:5].index
df = df_ads_mapdata[df_ads_mapdata["property_type"].isin(props)].copy()
df["price"] = df["price"] / 1000

bedroom_labels = ["1 bedroom","2 bedrooms","3 bedrooms","More than 3 bedrooms"]
bedrooms = pd.cut(df.beds,[0,1,2,3,99],labels=bedroom_labels)
bedrooms = bedrooms.to_frame()
bedrooms.columns = ['bedrooms']
df = pd.concat([df,bedrooms],axis = 1)

fig, axes = plt.subplots(2,2,sharey=True,figsize=(10,6))
for ax, label in zip(axes.flatten(), bedroom_labels):
    sns.barplot(x='price',y='property_type', data=df[df["bedrooms"]==label], estimator=np.mean, ci=None, ax=ax)
    ax.set(title=label, xlabel="Average price (x1000)", ylabel=None)

fig.suptitle('Property prices in Dublin')
fig.tight_layout()
fig.subplots_adjust(top=0.9)

plt.show()
fig.savefig("images/prices_property_type.png", dpi=300)

# Plotting average number of amenities

osm_vars = ['pubs', 'caferestaurants', 'schools', 'stations', 'platforms', 'parks', 'churches', 'health', 'sports', 'shops']

df = pd.melt(df_ads_mapdata[osm_vars],value_vars=osm_vars)

fig = plt.figure(figsize=(6,4))
ax = fig.add_subplot(111)
sns.barplot(x='value',y='variable', data=df, estimator=np.mean, ci=None)
plt.suptitle('Amenities in 500m radius')
plt.xlabel("Average count")
plt.ylabel(None)
plt.tight_layout()
fig.subplots_adjust(top=0.9)
plt.show()

fig.savefig("images/amenities.png", dpi=300)
