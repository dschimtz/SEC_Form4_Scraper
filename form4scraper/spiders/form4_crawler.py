import scrapy
import csv

class QuotesSpider(scrapy.Spider):
    name = "edgar_search"

    def start_requests(self):
        # Load in the CIKs used to locate a companie's filings
        with open(r'.\form4scraper\Example_Universe.csv', 'r') as f: 
            reader = csv.reader(f)
            urls = list(reader)
    
        ciks = [row[1] for row in urls]
        
        for i in range(len(ciks[101:200])):
            cik = "000{}".format(ciks[i])
            url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=&dateb=&owner=only&count=100".format(cik)
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(cik=cik, start=0))

    def parse(self, response, cik, start):
        def modify_start(start):
            return "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=&dateb=&owner=only&start={}&count=100".format(cik,start)
        
        next_page_selector = '//td/a[@id="documentsbutton"]/@href'
        
        if len(response.xpath(next_page_selector).extract()) == 0:
            return
        
        """
        yield {
            "len" : len(response.xpath(next_page_selector).extract()),
            "url" : response.url,
            "cik" : cik,
            "start" : start,
        }
        """
        
        next_pages = response.xpath(next_page_selector).extract()
        
        for i in next_pages:
            yield response.follow(i, self.parse_inter_page, cb_kwargs=dict(cik=cik))

        start += 100
        
        yield scrapy.Request(url=modify_start(start), callback=self.parse, cb_kwargs=dict(cik=cik, start=start))
        
    def parse_inter_page(self, response, cik):
        form4_selector = '//td[text()="4"]/preceding-sibling::td/a[contains(text(), ".xml")]/@href'
        form4_page = response.xpath(form4_selector).extract_first()
        if (form4_page is not None):
            yield response.follow(form4_page, self.parse_form4, cb_kwargs=dict(cik=cik))
        
    def parse_form4(self, response, cik):        
        yield {
            "Url"             : response.url,
            "CIK"             : cik, 
            "Owner"           : response.xpath('//rptOwnerName/text()').extract_first(),
            "Officer Title"   : response.xpath('//officerTitle/text()').extract_first(),
            "Period of Report": response.xpath('//periodOfReport/text()').extract_first(),
        }
