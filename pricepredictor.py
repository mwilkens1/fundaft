import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from add_data import Add_data
from sklearn.externals import joblib
import numpy as np

class PricePredictor():
    """
    Predict the price of a property that is advertised on daft.ie. The input
    is a URL from Daft.ie and the class can produce a predicted price.
    """
    
    def __init__(self):
        # Reads in the model to predict the price
        self.model = joblib.load("model/model.pkl")

    def parse_data(self, url):
        """
        Function to parse the data of a given Daft.ie URL

        Input:
        url = a URL of an ad on daft.ie

        Output:
        data = scraped data from daft.ie

        """
        # This header is required for Daft.ie
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/'
                            '537.36 (KHTML, like Gecko) Chrome/41.0.22'
                            '28.0 Safari/537.36'}

        # Get the page of the ad
        #r = requests.get(url, headers=headers, timeout=3)        
        attempt = 1
        max_attempts = 5
        while attempt <= max_attempts :
            try:
                r = requests.get(url, headers=headers, timeout=3)
                break
            except:                
                print("Attempt {} failed".format(attempt))
                if attempt==max_attempts:
                    print("Failed to retrieve data")
                    return
                attempt += 1 
        
        # Parse the content
        soup = BeautifulSoup(r.text, 'lxml')

        # All the data we need is stored in one javascript variable
        pattern = re.compile(r"var trackingParam = (.*?);$", 
                                re.MULTILINE | re.DOTALL)
        script = soup.find("script", text=pattern)
        data = pattern.search(script.text).group(1)

        # The data is converted into a dictionary 
        data_dict = eval(data.replace("null", "np.nan"))
        # and to a dataframe
        df = pd.DataFrame(data_dict, index=[0])
        
        # Sometimes the add does not include all the variables that the model
        # requires to predict the price. 
        # Check if any variables are missing and include them with np.nan
        cols_needed = ['environment', 'platform', 'page_name', 'area', 'county',
                       'longitude', 'latitude', 'seller_id', 'seller_name', 
                       'seller_type','selling_type', 'property_category', 
                       'ad_id','property_title','published_date','no_of_photos', 
                       'advertising_type','currency','price_type', 'price',
                       'bathrooms', 'beds', 'facility','open_viewing', 
                       'ber_classification', 'surface','property_type','ad_ids']

        # If any of the required columns are missing
        if pd.Series(cols_needed).isin(df.columns).all() == False:          
            
            # loop over each of the missing columns...
            i = 0 
            for col in pd.Series(cols_needed).isin(df.columns):
                if col == False:
                    #... and give them nan value
                    df[cols_needed[i]] = np.nan

                i += 1                

        # Then the data is enriched with the openstreetmap data and some 
        # recodes are applied
        add_data = Add_data(df)
        add_data.add_amenities()
        add_data.add_disctrics()
        add_data.recode()

        self.data = add_data.df_ads_mapdata

    def predict_price(self):

        try: # if data exists
            # Returns a predicted price
            self.predicted_price = np.exp(self.model.predict(self.data)[0])
            return(self.predicted_price)
        except: # else returns nothing
            return