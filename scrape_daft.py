import scrapy
from scrapy.crawler import CrawlerProcess
import re
import pandas as pd
import geopy.distance
import os
from datetime import datetime, date, time
from shutil import copyfile
import numpy as np

class Daft_spider(scrapy.Spider):
    """Crawler for Daft.ie using scrapy spider"""
    custom_settings = {
        'USER_AGENT': {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/'
                       '537.36 (KHTML, like Gecko) Chrome/41.0.22'
                       '28.0 Safari/537.36'},
        'LOG_LEVEL': "INFO",
    }
    name = 'daft'

    def parse(self, response):
        """Extract the links to all ads"""

        links = response.css('a.PropertyInformationCommonStyles__addressCopy--'
                             'link::attr(href)').extract()

        # Crawl into each of them and pass them the parse_ad function
        for link in links:
            yield response.follow(url = link, callback = self.parse_ad)

        # Go to the next page of ads
        for a in response.css('li.next_page > a::attr(href)'):
            yield response.follow(a, callback = self.parse)

    def parse_ad(self, response):
        """Parses data from the ads and appends it to list ads"""
        # Extracts a javascript variable that contains all info on the page
        ad_data=response.css('script:contains("trackingParam")::text').get()
        ad_data=re.findall(r'(?<=trackingParam = ).*?(?=;)', ad_data)[0]

        #self.ads.append(eval(ad_data))

        with open('scrape.txt', 'a') as f:
             f.write(ad_data + "\n")
        self.log('Saved file %s' % 'scrape.txt')

class Crawl_daft:

    def __init__(self):
        self.ads= []
        self.days_since_last_crawl=int()
        self.date_last_crawl=time()
        self.start_urls=[]
        self.data = pd.DataFrame()
     
    def create_url(self):
        """Calculates the number of days since the last crawl on the basis
        of the date when the df_ads_mapdata.pkl file was last modified. 
        Then, using the days since last crawl, it creates the starting URL for
        the crawler"""

        self.date_last_crawl=datetime.utcfromtimestamp(
            os.path.getmtime("data/df_ads_mapdata.csv")).date()
        timedelta = date.today() - self.date_last_crawl
        self.days_since_last_crawl = timedelta.days

        self.start_urls = 'https://www.daft.ie/dublin-city/property-for-sale/?' \
            'ad_type=sale&advanced=1&s%5Bdays_old%5D=' + \
            str(self.days_since_last_crawl-1) + \
            '&s%5Badvanced%5D=1&searchSource=sale'

        print("Days since last crawl: {}".format(self.days_since_last_crawl))
        print("URL: {}".format(self.start_urls))

    def crawl(self):
        process = CrawlerProcess()
        process.crawl(Daft_spider, start_urls=[self.start_urls]) 
        process.start()
        
        data = open('scrape.txt', 'r')
        with data as f:
            lines = f.read().splitlines()
        data.close()
        os.remove('scrape.txt')
        
        ads = []
        for i in lines:
            ads.append(eval(i.replace("null", "np.nan")))

        self.data = pd.DataFrame(ads)
