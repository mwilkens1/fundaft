import json
import pandas as pd
import numpy as np
import plotly

def return_figures(bedrooms, proptype):
    
    # Choropleth map
    with open("data/boundaries/ED.geojson") as json_file:
                geojson = json.load(json_file)
    df_ads_mapdata = pd.read_pickle('data/df_ads_mapdata.pkl')

    if bedrooms == "bed1":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.beds==1]
    if bedrooms == "bed2":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.beds == 2]
    if bedrooms == "bed3":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.beds == 3]
    if bedrooms == "bed4":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.beds >= 4]

    if proptype == "detached":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.property_type == "detached"]
    if proptype == "semi-detached":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.property_type == "semi-detached"]
    if proptype == "terraced":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.property_type ==  "terraced"]
    if proptype == "apartment":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.property_type == "apartment"]

    df = df_ads_mapdata.groupby("EDNAME")[['price']].median().reset_index()
    df["logprice"] = np.log(df.price)
    df["price"] = round(df.price, -3) / 1000

    df.to_pickle('data/data_for_mapplot.pkl')

    #Most expensive hoods
    fig1 = dict(locations=df.EDNAME, 
                    z=df.logprice, 
                    geojson=geojson,
                    price=df.price)

    df_expensive = df.sort_values("price", ascending=False).head().sort_values("price")
    fig2 = dict(x=df_expensive.price, y=df_expensive.EDNAME)

    #Least expensive hoods
    df_cheap = df.sort_values(
        "price", ascending=True).head().sort_values("price", ascending=False)
    fig3 = dict(x=df_cheap.price, y=df_cheap.EDNAME)

    #Price over time plot
    df = df_ads_mapdata.loc[df_ads_mapdata['published_date'] >= '05-2019']
    df = df.groupby("month")[['price']].median().reset_index()

    fig4 = dict(x=df.month,y=df.price)

    figures = []
    figures.append(fig1)
    figures.append(fig2)
    figures.append(fig3)
    figures.append(fig4)

    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    return(figuresJSON)
