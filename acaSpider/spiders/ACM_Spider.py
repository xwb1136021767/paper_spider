import scrapy
from scrapy.utils.project import get_project_settings
from acaSpider.items import AcaspiderItem
import logging
import re
import datetime
from acaSpider.proxyDownloader import getProxy

Periodicals = ['FAST', 'MSST', 'ATC', 'MASCOTS', 'SYSTOR', 'HPCA', 'ISCA', 'SOSP', 'OSDI',
               'NSDI', 'TOCS', 'TOS', 'TCAD', 'TC', 'TPDS', 'PPoPP', 'DAC', 'HPCA', 'MICRO',
               'SC', 'ISCA', 'USENIX ATC', 'JSAC', 'TMC', 'TON', 'SIGCOMM', 'MobiCom', 'INFOCOM',
               'NSDI', 'TDSC', 'TIFS', 'CCS', 'EUROCRYPT', 'S&P', 'CRYPTO', 'USENIX Security',
               'TOPLAS', 'TOSEM', 'TSE', 'PLDI', 'POPL', 'FSE/ESEC', 'OOPSLA', 'ASE', 'ICSE',
               'ISSTA', 'OSDI', 'TODS', 'TOIS', 'TKDE', 'VLDBJ'
               ]

CITE_LIMIT = 30


class ACMSpider(scrapy.Spider):
    name = "ACM_Spider"
    allowed_domains = ["dl.acm.org"]
    start_urls = get_project_settings().get('ACM_URL')

    def __init__(self):
        super(ACMSpider, self).__init__()
        self.startPage = 0
        self.pageSize = 20
        self.startTime = get_project_settings().get('START_TIME')
        self.proxyUpdateDelay = get_project_settings().get('PROXY_UPDATE_DELAY')
        getProxy().main()

    def parse(self, response):
        item = AcaspiderItem()
        print('爬取第', self.startPage, '页')

        results_num = response.xpath('//span[@class="hitsLength"]/text()').extract()[0].replace(',', '')
        subjects = response.xpath('//ul[@class="rlist--inline facet__list--applied"]/li/span/text()').extract()[0]
        response = response.xpath('//li[@class="search__item issue-item-container"]')
        item['title'] = []
        item['authors'] = []
        item['year'] = []
        item['typex'] = []
        item['subjects'] = []
        item['url'] = []
        item['abstract'] = []
        item['citation'] = []

        print('result_num = ')
        print(results_num)

        for res in response:

            # try:
            #     citation = res.xpath('.//span[@class="citation"]/span/text()').extract()[0]
            #     item['citation'].append(res.xpath('.//span[@class="citation"]/span/text()').extract()[0])
            # except:
            #     item['citation'].append(' ')

            try:

                citation = self.remove_html(res.xpath('.//span[@class="citation"]/span/text()').extract()[0])
                type = res.xpath('.//span[@class="epub-section__title"]/text()').extract()[0]
                print(citation)
                print(type)
                if_add = False
                for periodical in Periodicals:
                    if periodical in type:
                        if_add = True
                        break

                if int(citation) >= CITE_LIMIT:
                    if_add = True

                print(int(citation))

                if if_add:
                    item['typex'].append(type)
                    item['citation'].append(citation)
                else:
                    continue

                # item['typex'].append(res.xpath('.//span[@class="epub-section__title"]/text()').extract()[0])
            except:
                item['citation'].append(0)
                item['typex'].append(' ')

            try:
                titie_content = ""
                for text in res.xpath('.//span[@class="hlFld-Title"]/a/text()').extract():
                    titie_content += text
                item['title'].append(titie_content)
            except:
                item['title'].append(' ')

                # print(res.xpath('.//span[@class="hlFld-Title"]/a/text()').extract())
                # titie_content = ""
                # for part in res.xpath('.//span[@class="hlFld-Title"]/a/text()').extract():
                #     titie_content += self.remove_html(part)
                #
                # item['title'].append(titie_content)
                # context = res.xpath('.//span[@class="hlFld-Title"]/a/text()').extract()
                # print(context)
                # # pattern = re.compile(r'<[^>]+>')
                # # re.findall(pattern, context)
                # item['title'].append(self.remove_html(res.xpath('.//span[@class="hlFld-Title"]/a/text()').extract()[0]))

            # try:
            #     item['authors'].append(
            #         self.merge_authors(res.xpath('.//ul[@aria-label="authors"]/li/a/span/text()').extract()))
            # except:


            try:
                pattern = re.compile(r'[a-zA-Z]')
                content = self.remove4year(self.remove_html(res.xpath('.//span[@class="dot-separator"]').extract()[0]))
                year = re.sub(pattern, '', content)
                item['year'].append(year)

                # item['year'].append(self.remove4year(self.remove_html(res.xpath('.//span[@class="dot-separator"]').extract()[0])))
            except:
                item['year'].append(' ')

            try:
                item['url'].append(res.xpath('.//a[@class="issue-item__doi dot-separator"]/text()').extract()[0])
            except:
                item['url'].append(' ')

            item['authors'].append(' ')
            item['abstract'].append(' ')

            # try:
            #     item['abstract'].append(
            #         self.remove_html(res.xpath('.//div[contains(@class, "issue-item__abstract")]/p').extract()[0]))
            # except:
            #     item['abstract'].append(' ')

            # try:
            #     item['citation'].append(res.xpath('.//span[@class="citation"]/span/text()').extract()[0])
            # except:
            #     item['citation'].append(' ')

            item['subjects'].append(subjects)

        yield item
        logging.warning('$ ACM_Spider已爬取：' + str((self.startPage + 1) * self.pageSize))

        # if (datetime.datetime.now() - self.startTime).seconds > self.proxyUpdateDelay:
        #     getProxy().main()
        #     print('Delay')
        #     print('已爬取：', (self.startPage + 1) * self.pageSize)
        #     logging.warning('$ ACM_Spider runs getProxy')

        if (self.startPage + 1) * self.pageSize < int(results_num):
            self.startPage += 1
            next_url = self.start_urls[0] + '&startPage=' + str(self.startPage) + '&pageSize=' + str(self.pageSize)
            yield scrapy.Request(
                next_url,
                callback=self.parse,
            )

    def remove_html(self, string):

        pattern = re.compile(r'<[^>]+>')
        return (re.sub(pattern, '', string).replace('\n', '').replace('  ', '')).strip()

    def remove4year(self, string):
        return string.split(', ')[0]

    def merge_authors(self, au_list):
        au_str = ''
        for i in au_list:
            au_str += i + ','
        return au_str.strip(',')


'''
    def parse(self, response):
        item = AcaspiderItem()
        print('爬取第', self.startPage, '页')
        results_num = response.xpath('//span[@class="hitsLength"]/text()').extract()[0].replace(',', '')
        item['title'] = list(map(self.remove_html, response.xpath('//span[@class="hlFld-Title"]/a/text()').extract()))
        item['authors'] = list(map(self.remove_html, response.xpath('//ul[@aria-label="authors"]').extract()))
        item['year'] = list(map(self.remove4year, list(map(self.remove_html, response.xpath('//span[@class="dot-separator"]').extract()))))
        item['typex'] = response.xpath('//span[@class="epub-section__title"]/text()').extract()
        item['subjects'] = response.xpath('//ul[@class="rlist--inline facet__list--applied"]/li/span/text()').extract() * len(item['title'])
        item['url'] = response.xpath('//a[@class="issue-item__doi dot-separator"]/text()').extract()
        item['abstract'] = list(map(self.remove_html, response.xpath('//div[@class="issue-item__abstract truncate-text trunc-done"]/p').extract()))
        item['citation'] = response.xpath('//span[@class="citation"]/span/text()').extract()  # 动态变化

        yield item
        logging.warning('$ ACM_Spider已爬取：' + str((self.startPage + 1) * self.pageSize))

        if (datetime.datetime.now() - self.startTime).seconds > self.proxyUpdateDelay:
            getProxy().main()
            print('已爬取：', (self.startPage + 1) * self.pageSize)
            logging.warning('$ ACM_Spider runs getProxy')

        if (self.startPage + 1) * self.pageSize < int(results_num) and self.startPage < 1:
            self.startPage += 1
            next_url = self.start_urls[0] + '&startPage=' + str(self.startPage) + '&pageSize=' + str(self.pageSize)
            yield scrapy.Request(
                next_url,
                callback=self.parse,
            )
'''
