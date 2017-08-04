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



BRANCH = ['Ascott', 'Citadines', 'Somerset']
HEADER1="""Accept: */*
Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=utf-8"""


class YelpSpider(scrapy.Spider):
    name = "ctripcity"
    allowed_domains = ["english.ctrip.com"]
    start_urls = [
        'http://english.ctrip.com/',
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
        for city in range(400000, 550000):
            header = self.getJson(HEADER1, '\n', ':')
            body = 'city=%s&optionType=Intlcity&label=A4WaYPRV2kG1FafH_vBD6w&pageno=1&hotelid=0&allianceid=0&sid=0' %str(city)
            yield FormRequest('http://english.ctrip.com/Hotels/list/HotelJsonResult?label=A4WaYPRV2kG1FafH_vBD6w&isScrolling=true', headers = header, body = body, dont_filter=True, callback=self.parseListHotelPage1, method='POST', meta = {'idSearch': str(city)})
    def parseListHotelPage1(self, response):
        # inspect_response(response, self)
        idSearch = response.meta['idSearch']
        print('Searching for: %s' %idSearch)
        Result = json.loads(response.body)
        totalHotel = Result['ResultCount']
        if totalHotel > 0:
            print('-----------Get %s hotel' %totalHotel)
            yield {
                'id': idSearch,
                'total_hotel': totalHotel,
            }
