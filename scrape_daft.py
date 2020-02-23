import scrapy
from scrapy.crawler import CrawlerProcess
import re
import pandas as pd
import geopy.distance

class SpiderClassName(scrapy.Spider):
    # Required by daft
    custom_settings = {
      'USER_AGENT': {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'},
      'LOG_LEVEL': "INFO",
    }
    name = 'daft'
    start_urls = [
        'https://www.daft.ie/dublin-city/property-for-sale/?ad_type=sale&advanced=1&s%5Bdays_old%5D=11&s%5Badvanced%5D=1&searchSource=sale',
    ]

    def parse(self,response):
        # Extract all the adds on the page
        links = response.css('a.PropertyInformationCommonStyles__addressCopy--link::attr(href)').extract()
        # Crawl into each of them and pass them the parse_ad function
        for link in links:
            yield response.follow(url = link, callback = self.parse_ad)

        # Go to the next page of ads
        for a in response.css('li.next_page > a::attr(href)'):
            yield response.follow(a, callback=self.parse)

    def parse_ad(self, response):
        # Extracts a javascript variable that contains all information on the page
        ad_data = response.css('script:contains("trackingParam")::text').get()
        ad_data = re.findall(r'(?<=trackingParam = ).*?(?=;)',ad_data)[0]
        # Appending it to a list
        ads.append(eval(ad_data))

ads = []

process = CrawlerProcess()
process.crawl(SpiderClassName)
process.start()

# Convert list of dictionary
df_ads = pd.DataFrame(ads)

# Calculate distance to centre
hapenny = (53.346300, -6.263100)
df_ads["dist_to_centre"] = df_ads.apply(lambda x: geopy.distance.distance((x.latitude,x.longitude),hapenny).km, axis=1)

df_ads.to_pickle('df_ads.pkl')
