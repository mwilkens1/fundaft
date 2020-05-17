import json
import plotly
from flask import render_template, request, url_for, jsonify, Flask
from return_figures import return_figures
from pricepredictor import PricePredictor
import requests

app = Flask(__name__)

# Instantiating the price predictor class. This loads the model
ad = PricePredictor()

def get_ad_data(url):    
    """
    Get data from an ad on Daft.ie

    Input: url of the ad

    Returns:
    data: json containing the title of the ad, its estimated value, 
          the url to the image of the property and its asking price.

    """
    ad.get_soup(str(url))

    ad.parse_data()
    ad.get_image()
    ad.predict_price()

    title = ad.data.property_title[0]

    image_url = ad.image_url
    
    est_value = ad.predicted_price
    est_value = "€{0:.0f},000".format(round(est_value, -3)/1000)

    price = ad.data.price[0]
    price = "€{}".format(price)
    price = price[:-3] + "," + price[-3:]

    data = [title, est_value, image_url, price]

    return data

# The page should show the first listing in dublin city by default
# scraping the page with the listings in Dublin.
ad.get_soup("https://www.daft.ie/dublin-city/property-for-sale/")

# Getting the url to the first listed ad
initial_url = "https://www.daft.ie/" + ad.soup.findAll('a', {'class': 'PropertyInformationCommonStyles__propertyPrice--link'})[0]['href']


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Function for rendering the index page. It shows by default the estimated
    value of the top listed property on Daft.ie for dublin city.
    """

    # Returns the figures with default settings (no filters)
    figuresJSON = return_figures(0,"any","all")

    # Returns the data from the first ad on Daft.ie
    initial_ad_data = get_ad_data(initial_url)

    plot_data = ad.data[['pubs', 'caferestaurants', 'schools', 'stations',
                         'platforms', 'parks', 'churches', 'health', 'sports', 'shops']].transpose()

    plot_data = dict(x=list(plot_data.index), y=plot_data[0].tolist())

    return render_template('index.html',
                           figuresJSON=figuresJSON,
                           initial_ad_data=json.dumps(initial_ad_data),
                           amenities_data=json.dumps(plot_data))


@app.route('/change_ad_url', methods=['GET','POST'])
def change_ad_url():
    """
    Returns the data needed for the ad that the user wants to estimate a
    value another property pasted in the box
    """
    url = request.args.get('url', '')    

    text_data = get_ad_data(url)

    plot_data = ad.data[['pubs', 'caferestaurants', 'schools', 'stations',
                    'platforms', 'parks', 'churches', 'health', 'sports', 'shops']].transpose()
    
    plot_data = dict(x = list(plot_data.index), y = plot_data[0].tolist())

    return json.dumps([text_data,plot_data])

@app.route('/change_selection', methods=['GET', 'POST'])
def change_selection():    
    """
    Updates the plots depending on the seletions made by the user.
    """
    
    bedrooms = request.args.get('bedrooms')
    proptype = request.args.get('proptype')
    Q = request.args.get('Q')

    figuresJSON = return_figures(bedrooms, proptype, Q)

    return figuresJSON

# def main():
#     app.run(host='0.0.0.0', port=3001, debug=True)

# if __name__ == '__main__':
#     main()
