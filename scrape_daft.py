from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
#import scrapy
#from scrapy.crawler import CrawlerProcess
import re
import pandas as pd
import geopy.distance
import os
from datetime import datetime, date, time
from shutil import copyfile
import numpy as np
import json
from bs4 import BeautifulSoup

class Daft_spider():
    """Crawler for Daft.ie using scrapy spider"""

    def __init__(self):
        self.ads_scraped = 0
        self.date_last_crawl = time()
        self.data = pd.DataFrame()
        self.start_urls = 'https://www.daft.ie/property-for-sale/dublin-city?sort=publishDateDesc'
        self.date_last_crawl = datetime.utcfromtimestamp(
            os.path.getmtime("data/df_ads_mapdata.csv")).date()

        timedelta = date.today() - self.date_last_crawl
        self.days_since_last_crawl = timedelta.days
                
        # Start the webdriver
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument('log-level=3')
        self.desired_capabilities = options.to_capabilities()
        self.driver = webdriver.Chrome(
            desired_capabilities=self.desired_capabilities)

        # Accept cookies once (the main reason for using selenium)
        self.driver.get(self.start_urls)

        try:
            accept = self.driver.find_element_by_xpath(
                '//*[@id = "js-cookie-modal-level-one"]/div/main/div/button[2]')
            accept.click()
        except:
            pass

        # now we are on the first list of ads

    def crawl(self):
        """Loops over each page of ads until there are no more pages"""

        #start a new webdriver and accept cookies
        self.driver_parse = webdriver.Chrome(
             desired_capabilities=self.desired_capabilities)
        self.driver_parse.get(self.start_urls)

        try:
            accept = self.driver_parse.find_element_by_xpath(
                   '//*[@id = "js-cookie-modal-level-one"]/div/main/div/button[2]')
            accept.click()
        except:
            pass

        stop = False
        self.end_reached= False

        while stop==False and self.end_reached==False:

            # Retrieving al ad links on the page (from driver, not driver_parse)
            links = []
            for i in self.driver.find_elements_by_xpath('//*[@id="__next"]/main/div[3]/div[1]/ul/li/a'):
                links.append(i.get_attribute('href'))

            # Crawl into each of the ads and retrieve the data (with driver_parse)
            for link in links:
                self.parse_ad(link)

            # if all ads are scraped, go to the next page with driver until there is no next page.
            try: 
                next_page = self.driver.find_element_by_xpath(
                    '// *[@id="__next"]/main/div[3]/div[1]/div[2]/div/button[last()]')   
                next_page.click()
            except:
                stop==True
        
        self.driver_parse.quit()
        self.driver.quit()

        data = open('scrape.txt', 'r')
        with data as f:
            lines = f.read().splitlines()
        data.close()
        os.remove('scrape.txt')

        ads = []
        for i in lines:
            ads.append(eval(i.replace("null", "np.nan")))

        self.data = pd.DataFrame(ads)

    def parse_ad(self, link):

        self.driver_parse.get(link)

        # Get soup
        soup = BeautifulSoup(self.driver_parse.page_source, 'lxml')

        # if add is a multiunit listing, call parse add on the list of those


        try:
            test = self.driver_parse.find_element_by_class_name("PropertyPage__ContentSection-sc-14jmnho-3 QUUxi")
            
            #extract urls
            unit_links = []
            element = self.driver_parse.find_elements_by_xpath(
                '// *[@id="__next"]/main/div[3]/div[1]/div[1]/div[4]/a')
            for i in element:
                unit_links.append("https://www.daft.ie/" +
                                  i.get_attribute('href'))

            for unit in unit_links:
                self.parse_ad(unit)

            return

        except NoSuchElementException:
            pass

        # Extract a javascript variable that contains all info on the page
        #ad_data = re.findall(r'(?<=trackingParam = ).*?(?=;)', html)[0]
        data = json.loads(soup.find(
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
            ad_data['bathrooms'] = int(
                re.findall('\d+', data['numBathrooms'])[0])
        if 'numBedrooms' in data.keys():
            ad_data['beds'] = int(re.findall('\d+', data['numBedrooms'])[0])

        if 'facilities' in data.keys():
            facilities = ''
            for i in data['facilities']:
                facilities = facilities + i['name'] + ','
            ad_data['facility'] = facilities[:-1]

        if 'ber' in data.keys():
            ad_data['ber_classification'] = data['ber']['rating']
        if 'floorArea' in data.keys():
            ad_data['surface'] = data['floorArea']['value']
        if 'propertyType' in data.keys():
            ad_data['property_type'] = data['propertyType']

        if 'propertyOverview' in data.keys():
            ad_data['no_of_units'] = int(re.findall(
                '\d+', data['propertyOverview']['text'])[0])

        # Stop if date is equal to or before last crawl date
        ad_date = datetime.strptime(
            ad_data['published_date'], '%d/%m/%Y').date()

        date_check = ad_date - self.date_last_crawl

        if date_check.days <= 0:
            self.end_reached = True
            return

        # Write the data to textfile
        with open('scrape.txt', 'a') as f:
            f.write(str(ad_data) + "\n")

        self.ads_scraped += 1
        print('\rAds scraped: {}'.format(self.ads_scraped), end='')
