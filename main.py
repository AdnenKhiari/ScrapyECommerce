from scrapy.crawler import CrawlerProcess
import scrapy as sc
import re
#import twisted.internet.reactor as reactor

class Tnspider(sc.Spider):
    
    name = "TnSpiderLel"
    
    output_file = None
    
    custom_settings = {
        'FEED_EXPORT_ENCODING' : 'utf-8'
    }
    
    def match_href_in_click(st):
        s = re.search("(location.href='(.*)';)$",st)
        return s.group(2)
    
    def start_requests(self):
        yield sc.Request(url = "https://www.mytek.tn/",callback=self.getMainCategories)
        
    def getMainCategories(self,response):
        main_cats = response.xpath('//ul[@class="vertical-list clearfix"]/li/a/@href').extract()
        for url in main_cats:
            yield response.follow(url = url,callback = self.getSubCategories)
            
    def getSubCategories(self,response):
        #all_cats = map(Tnspider.match_href_in_click,response.xpath('//div[@id="headingOne"]//h5/@onclick').extract())
        all_cats = response.xpath('//div[@data-parent="#accordionExample"]//div[@class="card-body"]//li/a/@href').extract()
        for url in all_cats:
            yield response.follow(url = url,callback = self.parseFinalProductsPage)

        
    def parseFinalProductsPage(self,response):
        allitems = response.xpath('//tr[@class="item product product-item product-item-info"]')
        #print("Length is",len(allitems) )
        titles = allitems.xpath('.//strong[@class="product name product-item-name "]/a/text()').extract()
        #print("titles Length is",len(titles) )
        prices = list(map(lambda d: d.replace(',','.') ,allitems.xpath('.//span[@class="price-container price-final_price tax weee"]/span/span[@class="price"]/text()').extract()))
        #print("prices Length is",len(prices) )
        product_types = ','.join(response.xpath('//div[@class="breadcrumbs"]/ul[@class="items"]/li[contains(@class,"item category")]/*/text()').extract())
        next_page = response.xpath('.//a[@class="action  next"]/@href').extract_first()
        #print(next_page)
        #with open("./data"+next_page[-3:]+".txt",'w') as f:
        
        for i in range(len(titles)):
            l = f"{product_types},{titles[i]},{prices[i]}\n"
            Tnspider.output_file.write(l)
        if(next_page):
            yield response.follow(url = next_page,callback=self.parseFinalProductsPage)
            

crawler = CrawlerProcess()
Tnspider.output_file = open("./data.csv",'w' ,encoding='utf-8')
crawler.crawl(Tnspider)
crawler.start()
Tnspider.output_file.close()
