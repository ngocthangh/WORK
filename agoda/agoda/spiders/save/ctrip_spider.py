import scrapy
import json
import csv
import re
from slugify import slugify
from scrapy.shell import inspect_response
from scrapy.http import FormRequest
from dateutil import parser
import time
from datetime import date, timedelta
from langid.langid import LanguageIdentifier, model
from langdetect import detect_langs
from scrapy.http import TextResponse
from scrapy.selector import Selector
import time
from scrapy.loader import ItemLoader
from Ctrip.items import CtripItem

LANGUAGE = ['en', 'zh-tw', 'zh-cn', 'fr']
REVIEW_PER_PAGE = 10 
RATING_OUT_OF = '5'
BRANCH = ['Ascott', 'Citadines', 'Somerset']
# BRANCH = ['Grand Mercure Roxy Singapore']
HEADER = """Accept:*/*
Accept-Encoding:gzip, deflate
Accept-Language:en-US,en;q=0.8
Connection:keep-alive
Content-Type:application/x-www-form-urlencoded; charset=UTF-8"""
HEADER1="""Accept: */*
Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=utf-8"""
class YelpSpider(scrapy.Spider):
    name = "ctrip"
    allowed_domains = ["english.ctrip.com"]
    start_urls = [
        'http://english.ctrip.com',
    ]
    handle_httpstatus_list = [503]

    def __init__(self):
    #     self.db = connectMySQL()
    #     self.db.create_database()
    #     self.db.create_table()
        self.crawl_till_date = date.today() - timedelta(1)
        self.ids_seen = set()
        self.ids_rev = set()
        self.identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
    
    def parseTest(self, response):
        text = response.css('div#searchlist-header h1::text').extract_first().strip()
        if '0 available properties' not in text:
            yield{  'id': response.meta['id'],
                'text': text,
            }
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
        with open('citydata/ctripcity1.csv') as csvfile:
            cities = csv.reader(csvfile, quotechar='"', delimiter=',',
                         quoting=csv.QUOTE_ALL, skipinitialspace=True)
            for city in cities:
                if len(city) > 0:
                    idSearch = str(city[0])
                    header = self.getJson(HEADER1, '\n', ':')
                    body = 'city=%s&optionType=Intlcity&label=A4WaYPRV2kG1FafH_vBD6w&pageno=1&hotelid=0&allianceid=0&sid=0' %idSearch
                    yield FormRequest('http://english.ctrip.com/Hotels/list/HotelJsonResult?label=A4WaYPRV2kG1FafH_vBD6w&isScrolling=true', headers = header, body = body, dont_filter=True, callback=self.parseListHotelPage1, method='POST', meta = {'idSearch': idSearch})

    def parseListHotelPage1(self, response):
        # inspect_response(response, self)
        print('###########Searching for id: %s' %response.meta['idSearch'])
        HotelsPerPage = 15
        Result = json.loads(response.body)
        totalHotel = Result['ResultCount']
        totalPage = int(totalHotel/HotelsPerPage)
        if totalHotel % HotelsPerPage > 0:
            totalPage += 1
        cityId = response.meta['idSearch']
        listHotel = Result['HotelResultModel']
        print('-----------Get %s hotel' %str(totalHotel))
        for hotel in listHotel:
            hotelId = hotel['hotelId']
            Name = hotel['hotelName']
            DetailLink = 'http:' + (hotel['hotelUrl']).split('?')[0]
            for branch in BRANCH:
                if branch in Name:
                    if hotelId in self.ids_seen:
                        print("Duplicate item found: %s" % hotelId)
                        break
                    else:
                        # self.db.insert_hotel(hotelId, Name, DetailLink, self.crawl_till_date)
                        # yield{'hotelId': hotelId,
                        #         'url': DetailLink,
                        #         'name': Name,
                        #         }
                        data = "hotelid=%s&PageNo=1&ReviewType=All&IsImageOnly=false&IsContentOnly=1&IsRecommend=false&ThemeVBId=0&BaseRoomType=&SelectedLabel=4" %hotelId
                        formdata = self.getJson(data, '&', '=')
                        header = self.getJson(HEADER, '\n', ':')
                        yield FormRequest('http://english.ctrip.com/hotels/Detail/GetReviewListHtmlV2', headers = header, formdata = formdata, dont_filter=True, callback=self.parseCommentNum, method='POST',meta = {'hotelId':str(hotelId),'DetailLink':DetailLink, 'Name': Name, 'Page': 1}) 
                        self.ids_seen.add(hotelId)
                    break
        for i in range(2, totalPage + 1):
            header = self.getJson(HEADER1, '\n', ':')
            body = 'city=%s&optionType=Intlcity&label=A4WaYPRV2kG1FafH_vBD6w&pageno=%s&hotelid=0&allianceid=0&sid=0' %(cityId, i)
            yield FormRequest('http://english.ctrip.com/Hotels/list/HotelJsonResult?label=A4WaYPRV2kG1FafH_vBD6w&isScrolling=true', headers = header, body = body, dont_filter=True, callback=self.parseListHotelPage2, method='POST', meta = {'idSearch': cityId, 'page': i})
            
                
    def parseListHotelPage2(self, response):
        print('##Searching for id: %s - Page %s' %(response.meta['idSearch'], response.meta['page']))
        HotelsPerPage = 15
        Result = json.loads(response.body)
        totalHotel = Result['ResultCount']
        totalPage = int(totalHotel/HotelsPerPage)
        if totalHotel % HotelsPerPage > 0:
            totalPage += 1
        cityId = response.meta['idSearch']
        listHotel = Result['HotelResultModel']
        print('-----------Get %s hotel' %str(len(listHotel)))
        for hotel in listHotel:
            hotelId = hotel['hotelId']
            Name = hotel['hotelName']
            DetailLink = 'http:' + (hotel['hotelUrl']).split('?')[0]
            for branch in BRANCH:
                if branch in Name:
                    if hotelId in self.ids_seen:
                        print("Duplicate item found: %s" % hotelId)
                        break
                    else:
                        # self.db.insert_hotel(hotelId, Name, DetailLink, self.crawl_till_date)
                        # yield{'hotelId': hotelId,
                        #         'url': DetailLink,
                        #         'name': Name,}
                        data = "hotelid=%s&PageNo=1&ReviewType=All&IsImageOnly=false&IsContentOnly=1&IsRecommend=false&ThemeVBId=0&BaseRoomType=&SelectedLabel=4" %hotelId
                        formdata = self.getJson(data, '&', '=')
                        header = self.getJson(HEADER, '\n', ':')
                        yield FormRequest('http://english.ctrip.com/hotels/Detail/GetReviewListHtmlV2', headers = header, formdata = formdata, dont_filter=True, callback=self.parseCommentNum, method='POST',meta = {'hotelId':str(hotelId),'DetailLink':DetailLink, 'Name': Name, 'Page': 1}) 
                        self.ids_seen.add(hotelId)
                    break
    def parseCommentNum(self, response):
        # inspect_response(response, self)
        hotelId = response.meta['hotelId']
        DetailLink = response.meta['DetailLink']
        Name = response.meta['Name']
        review_count_text = response.css('div#reviewTagHidden li#reviewAll span::text').extract()
        if len(review_count_text) > 0:
            review_count_text = review_count_text[0].strip()
        else:
            review_count_text = ''
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" %review_count_text)
        nums = re.findall(r'\d+', review_count_text)
        print("@@@@@@@@@@@@@@@@@@@@@@@@ %s" %nums)
        totalReview = 0
        for n in nums:
            if int(n)>0:
                totalReview = int(n)
                break
        if totalReview > 0:
            print('################# Review Number: %s' %str(totalReview))
            totalPage = int(totalReview / REVIEW_PER_PAGE)
            if totalReview % REVIEW_PER_PAGE > 0:
                totalPage += 1
            print('################# Page Number: %s' %str(totalPage))
            for i in range(1, totalPage + 1):
                data = "hotelid=%s&PageNo=%s&ReviewType=All&IsImageOnly=false&IsContentOnly=1&IsRecommend=false&ThemeVBId=0&BaseRoomType=&SelectedLabel=4" %(hotelId, i)
                formdata = self.getJson(data, '&', '=')
                header = self.getJson(HEADER, '\n', ':')
                yield FormRequest('http://english.ctrip.com/hotels/Detail/GetReviewListHtmlV2', headers = header, formdata = formdata, dont_filter=True, callback=self.parseComment, method='POST',meta = {'hotelId':str(hotelId),'DetailLink':DetailLink, 'Name': Name}) 
                        
    def parseComment(self, response):
        hotelId = response.meta['hotelId']
        DetailLink = response.meta['DetailLink']
        Name = response.meta['Name']
        reviewList = response.css('ul.review-list')
        reviewItems = reviewList.css('li.review-item')
    
        for review in reviewItems:
            reviewInfo = review.css('div.review-user')
            reviewerName = reviewInfo.css('span.name::text').extract()
            if len(reviewerName) > 0:
                reviewerName = reviewerName[0].strip()
            else:
                reviewerName = ''

            ReviewDate = reviewInfo.css('span.time::text').extract()
            if len(ReviewDate) > 0:
                ReviewDate = ReviewDate[0].strip()
            else:
                ReviewDate = ''
            parser.parserinfo() 
            dateTimeStamp = parser.parse(ReviewDate)
            ReviewDateParse = date(dateTimeStamp.year, dateTimeStamp.month, dateTimeStamp.day)
            if (ReviewDateParse > self.crawl_till_date):
                continue
            dateTimeStamp = str(time.mktime(dateTimeStamp.timetuple()))

            reviewInfo2 = review.css('div.review-con')
            rev_score = reviewInfo2.css('div.score-overview span.score-num em::text').extract()
            if len(rev_score) > 0:
                rev_score = rev_score[0].strip()
            else:
                rev_score = ''

            ReviewText = reviewInfo2.css('div.review-cnt p[name="reviewContent"]::text').extract()
            if len(ReviewText) > 0:
                ReviewText = ReviewText[0].strip()
            else:
                ReviewText = ''
            Language = ''
            try:
                if(ReviewText != ''):
                    Lang_langid = self.identifier.classify(ReviewText)
                    Lang_langdetect = detect_langs(ReviewText)[0]
                    langid_pro = float(Lang_langid[1])
                    langdetect_pro = float(str(Lang_langdetect).split(':')[1])
                    
                pass
            except Exception as e:
                print('Can not detect language!')
            # if Language not in LANGUAGE:
            #     continue
            # if Language != 'en':

            rev = reviewerName + hotelId + dateTimeStamp + rev_score 
            if rev in self.ids_rev:
                print('Duplicate Review for: %s' %rev)
                continue
            it = ItemLoader(item=CtripItem())
            # it.add_value('title', ReviewTitle)
            it.add_value('text', ReviewText)
            it.add_value('detected_lang', Language)
            it.add_value('published_date_1', str(ReviewDateParse))
            it.add_value('published_date', dateTimeStamp)
            it.add_value('product_id', hotelId)
            it.add_value('rating', rev_score)
            it.add_value('rating_outof', RATING_OUT_OF)
            it.add_value('author', reviewerName)
            # it.add_value('country', reviewerNation)
            # it.add_value('reviewer_group', travelerType)
            # it.add_value('room_type', roomType)
            # it.add_value('stay_detail', detailStayed)
            it.add_value('url', DetailLink)
            # it.add_value('data_provider_id', providerId)
            it.add_value('product_name', Name)
            # self.db.insert_review(it)
            yield it.load_item()
            self.ids_rev.add(rev)