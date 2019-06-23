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
fig.savefig("images/prices_proporty_type.png")


for bed in bedroom_labels:
    sns.barplot(x='price',y='property_type', data=df[df["bedrooms"]==bed], estimator=np.mean, ci=None)







sns.boxplot(x=df["property_type"], y=df["price"], palette="Blues")

proptypes = ["detached","semi-detached","terraced","detached","apartment"]

for type in proptypes:
    subset = df_ads_mapdata[df_ads_mapdata["property_type"]==type]
    sns.distplot(subset['price'].dropna(), hist=False, kde=True, bins=100, kde_kws={'linewidth':3}, label=type)

plt.xscale('log')
plt.show()

#select 4 most common property types
props = df_ads_mapdata.property_type.value_counts()[0:4].index
df = df_ads_mapdata[df_ads_mapdata["property_type"].isin(props)]

sns.boxplot(y='price', x='property_type',  data=df,
                 palette="colorblind")
plt.xticks(rotation=90)
plt.ylim(0,4000000)
plt.show()


sns.distplot(df_ads_mapdata['price'].dropna(), hist=False, kde=True, bins=100, color = 'blue', hist_kws={'edgecolor':'black'})
# Add labels
plt.title('Histogram of Arrival Delays')
plt.xlabel('Delay (min)')
plt.ylabel('Flights')
