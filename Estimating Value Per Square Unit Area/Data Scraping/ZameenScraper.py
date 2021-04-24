# packages
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import urllib
import json

# zameen scraper class
class ZameenScraper(scrapy.Spider):
    # scraper/spider name
    name = 'zameen'
    
    # base URL
    base_url = 'https://www.zameen.com/Houses_Property/'
    
    # string query parameters
    params = {
        
        }
    
    # custom headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
        }
    
    # custom settings
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'zameen_khi_houses.csv',
        
        # uncomment below to limit the spider speed
        #'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        #'DOWNLOAD_DELAY': 1
        }
    
    # crawler's entry point
    def start_requests(self):
        # loop over the page range
        for page in range(1, 705):
            # generate next page URL
            next_page = self.base_url + 'Karachi-2-' + str(page) + '.html'
            next_page += urllib.parse.urlencode(self.params)
            
            # crawl the next page URL
            yield scrapy.Request(
                url = next_page,
                headers = self.headers,
                callback = self.parse
                )
        
        # parse property cards
    def parse(self, response):
        
        # The commented out portion below was used to save out the output of a page we wanted to parse to help with figuring out data extraction logic
        '''   
        # write HTML response to local file
        with open('res.html', 'w', encoding="utf-8") as f:
            f.write(response.text)
        '''
        
            
        '''      
        # local HTML content
        content = ''
        
        # load local HTML file to debug data extraction logic
        with open('res.html', 'r', encoding="utf-8") as f:
            for line in f.read():
                content += line
                    
        # initialize scrapy selector
        response = Selector(text = content)
        '''
        
        # features list
        features = []
        
        # loop over property cards data
        for card in response.css('li[role="article"]'):
            # data extraction logic
            feature = {
                'title': card.css('h2[aria-label="Title"]::text')
                             .get(),
                
                'price': card.css('span[aria-label="Price"]::text')
                             .get(),
                
                'location': card.css('div[aria-label="Location"]::text')
                                .get(),
                
                'details_url': 'https://www.zameen.com' + card.css('a::attr(href)')
                                   .get(),
                                   
                'bedrooms': card.css('span[aria-label="Beds"]::text')
                                .get(),
                
                'bathrooms': card.css('span[aria-label="Baths"]::text')
                                 .get(),
                                 
                'area': card.css('span[aria-label="Area"] *::text')
                            .get(),
                            
                'price': '',
                
                'latitude': '',
                
                'longitude': '',
                
                'precise_area': ''
                }
            
            # append next feature
            features.append(feature)
            
        # extract additional data from JavaScipt object notation data. Note that latitute and logitude for each property are not the lat/long of that property
        # but that of a nearby central position
        json_data = ''.join([
            script.get() for script in
            response.css('script::text')
            if 'window.state = ' in script.get()
        ])
            
        # extract JSON part
        try:    
            json_data = json_data.split('window.state =')[-1].split('}};')[0] + '}}'
                
            # parse JSON to dictionary
            json_data = json.loads(json_data)
                
            # extract cards data
            json_data = json_data['algolia']['content']['hits']
            
            # loop over the features
            for index in range(0, len(features)):
                features[index]['price'] = json_data[index]['price']
                features[index]['latitude'] = json_data[index]['geography']['lat']
                features[index]['longitude'] = json_data[index]['geography']['lng']
                features[index]['precise_area'] = json_data[index]['area']
                #print(json.dumps(features, indent=2))
                
                # write feature to output CSV file
                yield features[index]
            
        except:
            pass
            #print(features[index])
            
            #print(json.dumps(json_data[index], indent=2))
            #print(json.dumps(features[index], indent=2))
           
                
        #print(json.dumps(json_data['algolia']['content']['hits'], indent=2))
        #print(len(response.css('li[role="article"]')))
      
        
# main driver
if __name__ == '__main__':
    # run scraper
    process = CrawlerProcess()
    process.crawl(ZameenScraper)
    process.start()
    
    # debugging selectors
    #ZameenScraper.parse(ZameenScraper, '')
    
