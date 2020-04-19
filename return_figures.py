import json
import pandas as pd
import numpy as np
import plotly
import pickle

def return_figures(bedrooms, proptype, Q):
    
    bedrooms = int(bedrooms)

    #Load the data            
    df_ads_mapdata = pd.read_csv('data/df_ads_mapdata.csv')
    
    #Selection for the property type plot
    df_proptype = df_ads_mapdata[['price','property_type','beds','quarter']].copy()
    df_proptype["logprice"] = np.log(df_proptype.price)
    df_proptype = df_proptype[df_proptype['property_type'].isin(['apartment', 'detached',
                                                                 'semi-detached', 'terraced'])]

    #Selection for the bedrooms plot
    bedroom_labels = ["1", "2", "3", "4+"]
    br = pd.cut(df_ads_mapdata.beds, 
                      [0, 1, 2, 3, 99], labels=bedroom_labels).to_frame()
    br.columns = ['bedrooms']
    df_bedrooms = pd.concat([df_ads_mapdata, br], axis=1)
    df_bedrooms["logprice"] = np.log(df_bedrooms.price)

    #Filters based on selections in the app
    if Q != 'all':
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.quarter == Q]
        df_proptype = df_proptype[df_proptype.quarter == Q]   
        df_bedrooms = df_bedrooms[df_bedrooms.quarter == Q]
    if bedrooms != 0:
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.beds==bedrooms]
        df_proptype = df_proptype[df_proptype.beds == bedrooms]    
    elif bedrooms == 4:
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.beds >= bedrooms]
        df_proptype = df_proptype[df_proptype.beds >= bedrooms]
    if proptype == "detached":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.property_type == "detached"]
        df_bedrooms = df_bedrooms[df_bedrooms.property_type == "detached"]
    if proptype == "semi-detached":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.property_type == "semi-detached"]
        df_bedrooms = df_bedrooms[df_bedrooms.property_type == "semi-detached"]
    if proptype == "terraced":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.property_type ==  "terraced"]
        df_bedrooms = df_bedrooms[df_bedrooms.property_type == "terraced"]
    if proptype == "apartment":
        df_ads_mapdata = df_ads_mapdata[df_ads_mapdata.property_type == "apartment"]
        df_bedrooms = df_bedrooms[df_bedrooms.property_type == "apartment"]  

    #Take the median for a number of plots per district
    df = df_ads_mapdata.groupby("EDNAME")[['price']].median().reset_index()
    df["logprice"] = np.log(df.price)
    df["price"] = round(df.price, -3) / 1000    
    
    # Choropleth map 
    with open("data/boundaries/ED.geojson") as json_file:
                geojson = json.load(json_file)
    fig0 = dict(locations=df.EDNAME, 
                    z=df.logprice, 
                    geojson=geojson,
                    price=df.price)

    #Most expensive hoods
    df_expensive = df.sort_values("price", ascending=False).head().sort_values("price")
    fig1 = dict(x=df_expensive.price, y=df_expensive.EDNAME)

    #Least expensive hoods
    df_cheap = df.sort_values(
        "price", ascending=True).head().sort_values("price", ascending=False)
    fig2 = dict(x=df_cheap.price, y=df_cheap.EDNAME)

    #Price over time plot
    df_ads_mapdata.published_date = pd.to_datetime(
        df_ads_mapdata.published_date)
    df = df_ads_mapdata.loc[df_ads_mapdata['published_date'] >= '05-2019']
    df = df.groupby("published_date")['price'].mean().rolling(60).mean().reset_index().dropna()
    fig3 = dict(x=df.published_date, y=df.price) 

    #Property_types plot
    df_proptype = df_proptype.dropna(subset=['property_type', 'logprice'])
    #Order by price
    new_order = df_proptype.groupby(
        "property_type").price.median().sort_values(ascending=False).index.to_list()
    df_proptype = df_proptype.set_index('property_type', drop=False)
    df_proptype = df_proptype.loc[new_order]
    fig4 = dict(x=df_proptype.property_type, y=df_proptype.price)
    
    #bedrooms plot
    df_bedrooms = df_bedrooms.dropna(subset=['bedrooms', 'logprice'])   
    #Order by price
    new_order = df_bedrooms.groupby(
        "bedrooms").price.median().sort_values(ascending=False).index.to_list()
    df_bedrooms = df_bedrooms.set_index('bedrooms', drop=False)
    df_bedrooms = df_bedrooms.loc[new_order]
    fig5 = dict(x=df_bedrooms.bedrooms, y=df_bedrooms.price,
                price=df_bedrooms.price)

    figures = [fig0,fig1,fig2,fig3,fig4,fig5]   

    figuresJSON = json.dumps(figures, cls=plotly.utils.PlotlyJSONEncoder)

    return(figuresJSON)
