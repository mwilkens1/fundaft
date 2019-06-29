import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import folium
from folium.plugins import HeatMap

%matplotlib inline

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

sns.barplot(x='price',y='property_type', data=df, estimator=np.mean, ci=None, hue='bedrooms')
plt.ylabel(None)
plt.xlabel('Price (x1000)')
plt.legend(('1','2','3','3+'), loc='lower right', title='Bedrooms')
plt.title('Property prices in Dublin')
plt.tight_layout()
plt.savefig("images/prices_property_type.png", dpi=300)
plt.show()

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


# Plotting heatmap of price per square meter

hmap = folium.Map(location=[53.346300, -6.263100], zoom_start=12, )

df = df_ads_mapdata[["latitude","longitude","price","surface"]].dropna()

df["price_sqm"] = df.price / df.surface

hm_price_sqm = HeatMap( list(zip(df.latitude, df.longitude, df.price_sqm)),
                   min_opacity=0.2,
                   max_val=70000,
                   radius=20, blur=10,
                   max_zoom=1,
                 )

hmap.add_child(hm_price_sqm)

hmap.save('images/heatmap_price_sqm.html')

# Heatmap of price

hmap = folium.Map(location=[53.346300, -6.263100], zoom_start=12, )

df = df_ads_mapdata[["latitude","longitude","price"]].dropna()

hm_price = HeatMap( list(zip(df.latitude, df.longitude, df.price)),
                   min_opacity=0.2,
                   max_val=10000000,
                   radius=20, blur=10,
                   max_zoom=5,
                 )

hmap.add_child(hm_price)

hmap.save('images/heatmap_price.html')
