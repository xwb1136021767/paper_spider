import scrapy
from acaSpider.items import AcaspiderItem
from scrapy.utils.project import get_project_settings

'''
title = scrapy.Field()
authors = scrapy.Field()
year = scrapy.Field()
typex = scrapy.Field()
subjects = scrapy.Field()
url = scrapy.Field()
abstract = scrapy.Field()
citation = scrapy.Field()
'''

Periodicals = ['FAST', 'MSST', 'ATC', 'MASCOTS', 'SYSTOR', 'HPCA', 'ISCA', 'SOSP', 'OSDI',
               'NSDI', 'TOCS', 'TOS', 'TCAD', 'TC', 'TPDS', 'PPoPP', 'DAC', 'HPCA', 'MICRO',
               'SC', 'ISCA', 'USENIX ATC', 'JSAC', 'TMC', 'TON', 'SIGCOMM', 'MobiCom', 'INFOCOM',
               'NSDI', 'TDSC', 'TIFS', 'CCS', 'EUROCRYPT', 'S&P', 'CRYPTO', 'USENIX Security',
               'TOPLAS', 'TOSEM', 'TSE', 'PLDI', 'POPL', 'FSE/ESEC', 'OOPSLA', 'ASE', 'ICSE',
               'ISSTA', 'OSDI', 'TODS', 'TOIS', 'TKDE', 'VLDBJ', 'HotStorage'
               ]

CITE_LIMIT = 30


class IEEESpider(scrapy.Spider):
    name = "IEEE_Spider"
    allowed_domains = ["ieeexplore.ieee.org"]
    start_urls = get_project_settings().get('IEEE_URL')

    def parse(self, response):
        # Developing in progress
        item = AcaspiderItem()
        response = response.xpath('//div[@class="List-results-items"]')
        item['title'] = []
        item['authors'] = []
        item['year'] = []
        item['typex'] = []
        item['subjects'] = []
        item['url'] = []
        item['abstract'] = []
        item['citation'] = []
        print(len(response))
        for res in response:
            type = res.xpath('.//xpl-results-item/div/div[@class="col result-item-align"]/div[@class="description"]/a/text()').extract()[0]
            if_add = False
            for periodical in Periodicals:
                if periodical in type:
                    if_add = True
                    break
            if if_add:
                item['typex'].append(type)
            else :
                continue;

            # citation =

            item['title'].append(res.xpath('.//xpl-results-item/div/div/h2/a/text()').extract()[0])
            item['authors'].append(self.merge_authors(res.xpath('.//xpl-results-item/div/div[@class="col result-item-align"]/p[@class="author"]//span//xpl-modal//a//span//text()').extract()))
            item['year'].append(self.process4year(res.xpath('.//xpl-results-item/div/div[@class="col result-item-align"]/div[@class="description"]/div[@class="publisher-info-container"]/span/text()').extract()[0]))
            # item['typex'].append(res.xpath('.//xpl-results-item/div/div[@class="col result-item-align"]/div[@class="description"]/a/text()').extract()[0])
            item['subjects'].append(' ')
            item['url'].append('https://ieeexplore.ieee.org'+res.xpath('.//xpl-results-item/div/div/h2/a/@href').extract()[0])
            item['abstract'].append(res.xpath('.//div[@class="js-displayer-content u-mt-1 stats-SearchResults_DocResult_ViewMore hide"]/span/text()').extract()[0])
            item['citation'].append(str(-1))

        yield item

    def merge_authors(self, au_list):
        au_str = ''
        for i in au_list:
            au_str += i + ','
        return au_str.strip(',')

    def process4year(self, year):
        return year[year.index(': ') + 1:].strip()
