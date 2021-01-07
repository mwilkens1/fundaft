import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from add_data import Add_data
from sklearn.externals import joblib
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import json

class PricePredictor():
    """
    Predict the price of a property that is advertised on daft.ie. The input
    is a URL from Daft.ie and the class can produce a predicted price.
    """
    
    def __init__(self):
        # Reads in the model to predict the price
        self.model = joblib.load("model/model.pkl")

    def get_soup(self,url):
        """
        Function to get the soup from a Daft.ie ad

        Input:
        url = a URL of an ad on daft.ie

        Output:
        soup = scraped html of the ad
        """

        #Use selenium to bypass cookiewall     
        options = Options()
        options.headless = True        
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-dev-shm-usage")        

        #Only for heroku
        #CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
        #GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN')
        #options.binary_location = GOOGLE_CHROME_BIN
        
        #driver = webdriver.Chrome(
        #    executable_path=CHROMEDRIVER_PATH, options=options)
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(5)     

        attempt = 1
        max_attempts = 5
        while attempt <= max_attempts:

            driver.get(url)

            #allowing all cookies. This popup does not appear if accepted before
            try:
                accept = driver.find_element_by_xpath(
                    '//*[@id = "js-cookie-modal-level-one"]/div/main/div/button[2]')
                accept.click()  # accept cookies
            except:
                pass

            # Parse the content
            self.soup = BeautifulSoup(driver.page_source, 'lxml')

            if hasattr(self, 'soup')==False:
                print("Attempt {} failed".format(attempt))
                attempt += 1
                continue
            else:
                driver.quit()
                break


    def get_image(self):
        """Get the url of the image of the ad"""      

        #self.image_url = self.soup.find_all('img', 
        #style=lambda style: style and "max-height: 525px" in style)[0]['src']
        self.image_url = self.soup.find(
            'img', attrs={'data-testid': True})['src']

    def parse_data(self):
        """
        Function to parse the data of a given Daft.ie URL
        """

        data = json.loads(self.soup.find(
            'script', type='application/json').string)['props']['pageProps']['listing']

        # Create dictionary of relevant variables
        ad_data = {}

        if 'neighbourhoodGuide' in data.keys():
            ad_data['area'] = data['neighbourhoodGuide']['title'].replace(
                ' Neighbourhood Guide', '')
        if 'point' in data.keys():
            ad_data['longitude'] = data['point']['coordinates'][0]
            ad_data['latitude'] = data['point']['coordinates'][1]
        if 'seller' in data.keys():
            ad_data['seller_id'] = data['seller']['sellerId']
            ad_data['seller_name'] = data['seller']['name']
            ad_data['seller_type'] = data['seller']['sellerType']
        if 'sellingType' in data.keys():
            ad_data['selling_type'] = data['sellingType']

        ad_data['ad_id'] = data['id']
        ad_data['property_title'] = data['title']
        ad_data['published_date'] = data['lastUpdateDate']

        if 'From' in data['price']:
            ad_data['price_type'] = 'from'
        if 'Price on Application' in data['price']:
            ad_data['price_type'] = 'on-application'

        ad_data['price'] = int(re.findall(
            '\d+', data['price'].replace(',', ''))[0])

        if 'numBathrooms' in data.keys():
            ad_data['bathrooms'] = float(
                re.findall('\d+', data['numBathrooms'])[0])
        if 'numBedrooms' in data.keys():
            ad_data['beds'] = float(re.findall('\d+', data['numBedrooms'])[0])

        if 'facilities' in data.keys():
            facilities = ''
            for i in data['facilities']:
                facilities = facilities + i['name'] + ','
            ad_data['facility'] = facilities[:-1]
        else:
            ad_data['facility'] = ''

        if 'ber' in data.keys():
            if data['ber']['rating'] == 'SI_666' or data['ber']['rating'] =='Exempt':
                ad_data['ber_classification'] = 'SINo666of2006exempt'
            else:
                ad_data['ber_classification'] = data['ber']['rating']     

        if 'floorArea' in data.keys():
            ad_data['surface'] = data['floorArea']['value']
        if 'propertyType' in data.keys():
            if data['propertyType'] == 'Terrace':
                ad_data['property_type'] = 'terraced'
            elif data['propertyType'] == 'End of Terrace':
                ad_data['property_type'] = 'end-of-terrace'
            elif data['propertyType'] == 'Bungalow':
                ad_data['property_type'] = 'bungalow'
            elif data['propertyType'] == 'Semi-D':
                ad_data['property_type'] = 'semi-detached'
            elif data['propertyType'] == 'House':
                ad_data['property_type'] = 'house'
            elif data['propertyType'] == 'Site':
                ad_data['property_type'] = 'site'
            else:
                ad_data['property_type'] = data['propertyType']

        if 'propertyOverview' in data.keys():
            ad_data['no_of_units'] = int(re.findall(
                '\d+', data['propertyOverview']['text'])[0])

        df = pd.DataFrame(ad_data, index=[0])

        # Sometimes the add does not include all the variables that the model
        # requires to predict the price. 
        # Check if any variables are missing and include them with np.nan
        cols_needed = ['area', 'longitude', 'latitude', 'seller_id', 'seller_name', 
                       'seller_type','selling_type',
                       'ad_id','property_title','published_date',
                       'price_type', 'price',
                       'bathrooms', 'beds', 'facility', 
                       'ber_classification', 'surface','property_type',
                       'no_of_units']

        # If any of the required columns are missing
        if pd.Series(cols_needed).isin(df.columns).all() == False:          
            
            # loop over each of the missing columns...
            i = 0 
            for col in pd.Series(cols_needed).isin(df.columns):
                if col == False:
                    #... and give them nan value
                    # Then the imputers in the pipeline will take
                    # care of the rest
                    df[cols_needed[i]] = np.nan

                i += 1                

        # For the facilities variable, dummies are created in the prep data
        # transformer. However, if some categories are not there they won't be
        # created.This is corrected here by setting them to np.nan. Imputer 
        # will take take of the rest.
        facilities = ['Alarm', 'Gas Fired Central Heating', 
            'Oil Fired Central Heating',
            'Parking', 'Wheelchair Access', 'Wired for Cable Television']
         
        if df.facility[0]=='':
            for facility in facilities:
                df[facility] = np.nan

        # Setting the price type to 'normal'. In case the ad for example has a 
        # 'range' or 'starting from' price type, we want the prediction to
        # reflect the actual worth, not the price you would expect given the 
        # price type. 
        df['price_type'] = 'Normal'

        # Then the data is enriched with the openstreetmap data and some 
        # recodes are applied
        add_data = Add_data(df)
        add_data.add_amenities()
        add_data.add_disctrics()
        add_data.recode()
       
        self.data = add_data.df_ads_mapdata


    def predict_price(self):
        """
        Predicts price of property given the data in the ad enriched with
        openstreetmap data

        Returns the predicted price
        """

        try: # if data exists
            # Returns a predicted price
            self.predicted_price = np.exp(self.model.predict(self.data)[0])
            return(self.predicted_price)
        except: # else returns 0
            self.predicted_price = 0
            return(self.predicted_price)
