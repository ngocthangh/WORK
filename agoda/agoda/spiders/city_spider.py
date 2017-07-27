import scrapy
import json
from msvcrt import getch
import csv
import re
from slugify import slugify
from scrapy.shell import inspect_response
from scrapy.http import FormRequest
from dateutil import parser
import time
from langdetect import detect
from scrapy.http import TextResponse
from scrapy.selector import Selector
import time
from scrapy.loader import ItemLoader
from agoda.items import AgodaReviewItem


BRANCH = ['Ascott', 'Citadines', 'Somerset']
HEADER = """Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest"""


class YelpSpider(scrapy.Spider):
    name = "agodacity"
    allowed_domains = ["agoda.com"]
    start_urls = [
        'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064',
    ]
    handle_httpstatus_list = [503]

    def getJson(self, data, deli, center):
        data1 = data.split(deli)
        data = '{ '
        for d in data1:
            if len(d.split(center)) > 1:
                data += '\"' + d.split(center)[0].strip() + '\":\"' + d.split(center)[1].strip() + '\"' + ','
            else:
                data += '\"' + d.split(center)[0].strip() + '\":\"\"' + ','
        data = data[:-1] + ' }'
        return json.loads(data)
    def parse(self, response):
        for city in range(0, 720000):
            header = self.getJson(HEADER, '\n', ':')
            data1 = "SearchType=1&ObjectID=0PlatformID=1001&CurrentDate=2017-07-24&CityId=%s&PageNumber=1&PageSize=45&SortType=0&IsSortChanged=false&SortByAsd=false&ReviewTravelerType=0&IsAllowYesterdaySearch=false&CultureInfo=en-US&UnavailableHotelId=0&Adults=1&Children=0&Rooms=1&CheckIn=2017-08-02&LengthOfStay=1&ChildAgesStr=&ExtraText=&IsDateless=false" %str(city)
            formdata = self.getJson(data1, '&', '=')
            yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', headers = header, formdata = formdata, dont_filter=True, callback=self.parseListHotelPage1, method='POST', meta = {'idSearch': str(city)})
    def parseListHotelPage1(self, response):
        # inspect_response(response, self)
        idSearch = response.meta['idSearch']
        print('Searching for: %s' %idSearch)
        Result = json.loads(response.body)
        totalHotel = Result['TotalFilteredHotels']
        if totalHotel > 0:
            print('-----------Get %s hotel' %totalHotel)
            yield {
                'id': idSearch,
                'total_hotel': totalHotel,
            }
