#import plotly.express as px
import json
import pandas as pd

#def return_figures():

    # Opening geojson
#    with open("data/boundaries/ED.geojson") as json_file:
#                areas = json.load(json_file)
#    df = pd.read_pickle('data/data_for_mapplot.pkl')

#    fig_map = px.choropleth_mapbox(df, geojson=areas, color="logprice",
#                            locations="EDNAME", featureidkey="properties.EDNAME",
#                            center={"lat": 53.324, "lon": -6.3},
#                            mapbox_style="carto-positron", zoom=10,
#                            color_continuous_scale=px.colors.sequential.YlOrRd,
#                            opacity=0.6,
#                            hover_data=['price'],
#                            labels={'EDNAME': 'Area',
#                                    'price': "<b>Median price(€)</b>", 
#                                    'logprice': "Median price (log)"},
#                            width=1000, height=850)
#    fig_map.layout.coloraxis.showscale = False


#    figures = []
#    figures.append(fig_map)

#    return(figures)


def return_figures():
    
    # Opening geojson
    with open("data/boundaries/ED.geojson") as json_file:
                geojson = json.load(json_file)
    df = pd.read_pickle('data/data_for_mapplot.pkl')

    figures = [dict(locations=df.EDNAME, 
                    z=df.logprice, 
                    geojson=geojson,
                    price=df.price / 1000)]

    return(figures)