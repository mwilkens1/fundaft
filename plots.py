import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

df_ads_mapdata = pd.read_pickle('df_ads_mapdata.pkl')

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
    ax.set(title=label, xlabel="Mean price (x1000)", ylabel=None)

fig.suptitle('Property prices in Dublin')
fig.tight_layout()
fig.subplots_adjust(top=0.9)

plt.show()
fig.savefig("images/prices_property_type.png")
