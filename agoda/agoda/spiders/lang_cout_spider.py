import scrapy
import json
from msvcrt import getch
import csv
import re
from slugify import slugify
from scrapy.shell import inspect_response
from scrapy.http import FormRequest
from translate import Translator


class YelpSpider(scrapy.Spider):
    name = "langcount"
    allowed_domains = ["agoda.com"]
    start_urls = [
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=DK&cid=-1&tag=&gclid=&aid=130243&userId=a45dbc08-94c8-4883-8267-14e589793930&languageId=1&sessionId=fn0s5opvtin15we2ijf5j20s&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2017-07-13&checkOut=2017-08-10&los=28&rooms=1&adults=1&children=0&childages=&ckuid=a45dbc08-94c8-4883-8267-14e589793930',
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=DK&cid=-1&tag=&gclid=&aid=130243&userId=a45dbc08-94c8-4883-8267-14e589793930&languageId=1&sessionId=fn0s5opvtin15we2ijf5j20s&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2018-02-15&checkOut=2018-02-16&los=1&rooms=1&adults=2&children=0&childages=&ckuid=a45dbc08-94c8-4883-8267-14e589793930',
        'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064',
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=VN&cid=-1&tag=&gclid=&aid=130243&userId=63298666-127d-4bdb-9a86-8c5cebd1d002&languageId=1&sessionId=gboizgbattkxku2rwguqlhbp&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2017-08-15&checkOut=2017-08-16&los=1&rooms=1&adults=2&children=0&childages=&ckuid=63298666-127d-4bdb-9a86-8c5cebd1d002&sort=agodaRecommended&PageNumber=5',

    ]
    handle_httpstatus_list = [503]
    def parse(self, response):
        with open('AgodaReviews.csv') as csvfile:
            texts = csv.reader(csvfile, quotechar='"', delimiter=',',
                         quoting=csv.QUOTE_ALL, skipinitialspace=True)
            # EN = 0
            # FR = 0
            # ZH = 0
            # for text in texts:
            #     lang = text[15]
            #     country = text[4]
            #     print('Lang: %s' % lang)
            #     if (lang == 'en' or lang == 'so' or lang == 'it' or lang == 'sk' or lang == 'pl'):
            #         EN += 1
            #     elif (lang == 'fr'):
            #         FR += 1
            #     elif (lang == 'zh-cn' or lang == 'zh-tw' or lang == 'ko') :
            #         ZH += 1
            #     elif (lang == 'ro'):
            #         if country == 'China' or country == 'Taiwan':
            #             ZH += 1
            #         else:
            #             EN += 1
            # ALL = EN + FR + ZH
            # print ('############################################################################################')
            # print('ALL: %s' %ALL)
            # print ('EN: %s : %s' %(EN, 100*(float(EN/ALL))))
            # print ('FR: %s : %s' %(FR, 100*(float(FR/ALL))))
            # print ('ZH: %s : %s' %(ZH, 100*(float(ZH/ALL))))
            
            MAX_TIME = 0
            MIN_TIME = 0
            i = 0
            for text in texts:
                i += 1
                if i == 1:
                    continue
                if i == 2:
                    MAX_TIME = int(text[10].split('.')[0])
                    MIN_TIME = int(text[10].split('.')[0])
                    continue
                print(i)
                timestamp = int(text[10].split('.')[0])
                if (timestamp > MAX_TIME):
                    MAX_TIME = timestamp
                if (timestamp < MIN_TIME):
                    MIN_TIME = timestamp

            TOTAL = MAX_TIME - MIN_TIME
            print('MAX : %s' %MAX_TIME)
            print('MIN : %s' %MIN_TIME)
            print('TOTAL TIMESTAMP : %s' %TOTAL)
            print('TOTAL DAY: %s' %(TOTAL/(3600*24)))