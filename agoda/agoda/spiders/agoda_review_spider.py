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
from langdetect import detect
from scrapy.http import TextResponse
from scrapy.selector import Selector
import time
from scrapy.loader import ItemLoader
from agoda.items import AgodaReviewItem
from queryMySQL import connectMySQL

CONFIG = []
REVIEW_PER_PAGE = 50
RATING_OUT_OF = '{"0":10}'
BRANCH = ['Ascott', 'Citadines', 'Somerset', 'otel', 'um']
LANGUAGE = '[1,2,7,8,20]'
# LANGUAGE = '[]'
HEADER = """Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest"""
HEADER_REVIEW = """Host: www.agoda.com
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0
Accept: text/html, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/json; charset=utf-8
X-Requested-With: XMLHttpRequest"""
class YelpSpider(scrapy.Spider):
    name = "agodareview"
    allowed_domains = ["agoda.com"]
    start_urls = [
        'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064',
    ]
    handle_httpstatus_list = [503]

    def __init__(self):
        self.db = connectMySQL()
        self.db.create_database()
        self.db.create_table()
        self.crawl_till_date = date.today() - timedelta(1)
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
        # return self.readConfiguration()
        # with open('citydata/AgodaCitys4.csv') as csvfile:
        with open('citydata/test.csv') as csvfile:
            cities = csv.reader(csvfile, quotechar='"', delimiter=',',
                         quoting=csv.QUOTE_ALL, skipinitialspace=True)
            for city in cities:
                if len(city) > 0:
                    idSearch = str(city[0])
                    header = self.getJson(HEADER, '\n', ':')
                    # data0 = "SearchType=1&CityId=%s&PageNumber=1&PageSize=45&SortType=0&CultureInfo=en-US&HasFilter=false&Adults=1&Children=0&Rooms=1&CheckIn=2017-07-29&LengthOfStay=1&ChildAgesStr=" %city[1]
                    data1 = "SearchType=1&ObjectID=0PlatformID=1001&CurrentDate=2017-07-24&CityId=%s&PageNumber=1&PageSize=45&SortType=0&IsSortChanged=false&SortByAsd=false&ReviewTravelerType=0&IsAllowYesterdaySearch=false&CultureInfo=en-US&UnavailableHotelId=0&Adults=1&Children=0&Rooms=1&CheckIn=2017-08-02&LengthOfStay=1&ChildAgesStr=&ExtraText=&IsDateless=false" %idSearch
                    formdata = self.getJson(data1, '&', '=')
                    yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', headers = header, formdata = formdata, dont_filter=True, callback=self.parseListHotelPage1, method='POST', meta = {'idSearch': idSearch})

    def parseListHotelPage1(self, response):
        # inspect_response(response, self)
        print('###########Searching for id: %s' %response.meta['idSearch'])
        Result = json.loads(response.body)
        totalPage = Result['TotalPage']
        page = Result['PageNumber']
        cityId = Result['SearchCriteria']['CityId']
        listHotel = Result['ResultList']
        print('-----------Get %s hotel' %str(len(listHotel)))
        for hotel in listHotel:
            hotelId = hotel['HotelID']
            Name = hotel['EnglishHotelName']
            for branch in BRANCH:
                if branch in Name:
                    DetailLink = 'https://www.agoda.com' + (hotel['HotelUrl']).split('?')[0]
                    self.db.insert_hotel(hotelId, Name, DetailLink, self.crawl_till_date)
                    # yield{'hotelId': hotelId}
                    # payload = {"hotelId": str(hotelId),"page":'1', "pageSize":'1',"sorting":'1',"filters":{"language":[],"room":[]}}
                    body = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":1,"sorting":1,"filters":{"language":' + LANGUAGE + ',"room":[]}}'
                    header = self.getJson(HEADER_REVIEW, '\n', ':')
                    # yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body, headers = header, dont_filter=True, callback=self.parseCommentNum, method='POST', meta = {'hotelId':str(hotelId),'DetailLink':DetailLink, 'Name': Name})
                    break
        for i in range(2, totalPage + 1):
            header = self.getJson(HEADER, '\n', ':')
            data0 = "SearchType=1&CityId=%s&PageNumber=%s&PageSize=45&SortType=0&CultureInfo=en-US&HasFilter=false&Adults=1&Children=0&Rooms=1&CheckIn=2017-07-29&LengthOfStay=1&ChildAgesStr=" %(cityId, i)
            formdata = self.getJson(data0, '&', '=')
            yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', headers = header, formdata = formdata, dont_filter=True, callback=self.parseListHotelPage2, method='POST')
            
                
    def parseListHotelPage2(self, response):
        Result = json.loads(response.body)
        listHotel = Result['ResultList']
        for hotel in listHotel:
            hotelId = hotel['HotelID']
            Name = hotel['EnglishHotelName']
            for branch in BRANCH:
                if branch in Name:
                    print('######################################### id : Name: %s : %s' %(hotelId, Name))
                    DetailLink = 'https://www.agoda.com' + (hotel['HotelUrl']).split('?')[0]
                    self.db.insert_hotel(hotelId, Name, DetailLink, self.crawl_till_date)
                    # payload = {"hotelId": str(hotelId),"page":'1',"pageSize":'1',"sorting":'1',"filters":{"language":[],"room":[]}}
                    # yield{'hotelId': hotelId}
                    body = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":1,"sorting":1,"filters":{"language":' + LANGUAGE + ',"room":[]}}'
                    header = self.getJson(HEADER_REVIEW, '\n', ':')
                    # yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body, headers = header, dont_filter=True, callback=self.parseCommentNum, method='POST', meta = {'hotelId':str(hotelId),'DetailLink':DetailLink, 'Name': Name})
    def parseCommentNum(self, response):
        # inspect_response(response, self)
        Bodys = response.css('div#hotelreview-detail-item')
        Body = Bodys[0]
        totalReview = 0
        for bd in Bodys:
            totalRe = bd.css('::attr(data-totalindex)').extract()
            if len(totalRe) > 0:
                totalReview = int(totalRe[0])
                if totalReview > 0:
                    Body = bd
                    break
        providerId = Body.css('::attr(data-review-provider)').extract()
        if len(providerId) > 0:
            providerId = providerId[0]
        else:
            providerId = ''
        hotelId = response.meta['hotelId']
        
        print('################# Review Number: %s' %str(totalReview))
        pageNumber = totalReview / REVIEW_PER_PAGE
        if totalReview % REVIEW_PER_PAGE > 0:
            pageNumber += 1
        print('################# Page Number: %s' %str(pageNumber))
        DetailLink = response.meta['DetailLink']
        Name = response.meta['Name']
        for i in range(1, pageNumber + 1):
            # payload = {"hotelId":str(hotelId),"page":str(i),"pageSize":str(REVIEW_PER_PAGE),"sorting":"1","filters":{"language":[2,7,8,20],"room":[]}}
            body = '{"hotelId":'+str(hotelId)+',"page":'+str(i)+',"pageSize":'+str(REVIEW_PER_PAGE)+',"sorting":1,"filters":{"language":' + LANGUAGE + ',"room":[]}}'
            header = self.getJson(HEADER_REVIEW, '\n', ':')
            yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'page':i, 'DetailLink': DetailLink, 'providerId': providerId, 'Name': Name})
                        
    def parseComment(self, response):
        # inspect_response(response, self)
        Body = response.css('div#hotelreview-detail-item')

        Reviews = Body.css('div.review-comment-items div.individual-review-item') 
        for re in Reviews:
            reId = re.css('::attr(data-id)').extract()
            if len(reId) > 0:
                reId = reId[0]
            else:
                reId = ''

            reInfo = re.css('div.review-info')
            reDetail = re.css('div.nopadding-right div.review-comment-bubble')

            ReviewDate = reDetail.css('div.comment-date-only div.comment-date span::text').extract()
            if len(ReviewDate) <= 0:
                ReviewDate = reDetail.css('div.comment-date-translate div.comment-date span::text').extract()
            if len(ReviewDate) > 0:
                ReviewDate = ReviewDate[0].strip().split('Reviewed')
                if len(ReviewDate) > 1:
                    ReviewDate = ReviewDate[1].strip()
            else:
                ReviewDate = ''
            parser.parserinfo(dayfirst=True) 
            dateTimeStamp = parser.parse(ReviewDate)
            d = date(dateTimeStamp.year, dateTimeStamp.month, dateTimeStamp.day)
            if (d > self.crawl_till_date):
                continue
            dateTimeStamp = str(time.mktime(dateTimeStamp.timetuple()))


            reScore = reInfo.css('div.comment-score span::text').extract()
            if len(reScore) > 0:
                reScore = reScore[0]
            else:
                reScore = ''

            reviewerName = reInfo.css('div[data-selenium="reviewer-name"] span strong::text').extract()
            if len(reviewerName) > 0:
                reviewerName = reviewerName[0].strip()
            else:
                reviewerName = ''

            reviewerNation = reInfo.css('div[data-selenium="reviewer-name"] span::text').extract()
            if len(reviewerNation) > 1:
                reviewerNation = reviewerNation[1].strip().split('from')
                if len(reviewerNation) > 1:
                    reviewerNation = reviewerNation[1].strip()
            else:
                reviewerNation = ''

            travelerType = reInfo.css('div[data-selenium="reviewer-traveller-type"] span::text').extract()
            if len(travelerType) > 0:
                travelerType = travelerType[0].strip()
            else:
                travelerType = ''

            roomType = reInfo.css('div[data-selenium="review-roomtype"] span::text').extract()
            if len(roomType) > 0:
                roomType = roomType[0].strip()
            else:
                roomType = ''

            detailStayed = reInfo.css('div[data-selenium="reviewer-stay-detail"] span::text').extract()
            if len(detailStayed) > 0:
                detailStayed = detailStayed[0].strip()
            else:
                detailStayed = ''

            
            ReviewTitle = reDetail.css('div.comment-title div.comment-title-text::text').extract()
            if len(ReviewTitle) > 0:
                ReviewTitle = ReviewTitle[0].strip()[:-1]
            else:
                ReviewTitle = ''

            ReviewText = ''
            PositiveReview = ''
            CommentReview = reDetail.css('div.comment-icon span::text').extract()
            if len(CommentReview) > 0:
                PositiveReview = CommentReview[0].strip()
                ReviewText += 'P: ' + PositiveReview
            
            NegativeReview = ''
            if len(CommentReview) > 1:
                NegativeReview = CommentReview[1].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += 'N: ' + NegativeReview

            ReviewText1 = reDetail.css('div.comment-text span::text').extract()
            if len(ReviewText1) > 0:
                ReviewText1 = ReviewText1[0].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += 'G: ' + ReviewText1
            else:
                ReviewText1 = ''
            
            
            Language = ''
            try:
                if(ReviewText != ''):
                    Language = detect(ReviewTitle + PositiveReview + NegativeReview + ReviewText1)
                pass
            except Exception as e:
                print('Can not detect language!')

            hotelId = response.meta['hotelId']
            DetailLink = response.meta['DetailLink']
            providerId = response.meta['providerId']
            Name = response.meta['Name']

            it = ItemLoader(item=AgodaReviewItem())
            it.add_value('title', ReviewTitle)
            it.add_value('text', ReviewText)
            it.add_value('detect_lang', Language)
            it.add_value('published_date_1', ReviewDate)
            it.add_value('published_date', dateTimeStamp)
            it.add_value('product_id', hotelId)
            it.add_value('rating', reScore)
            it.add_value('rating_outof', RATING_OUT_OF)
            it.add_value('author', reviewerName)
            it.add_value('country', reviewerNation)
            it.add_value('reviewer_group', travelerType)
            it.add_value('room_type', roomType)
            it.add_value('stay_detail', detailStayed)
            it.add_value('url', DetailLink)
            it.add_value('data_provider_id', providerId)
            it.add_value('product_name', Name)
            yield it.load_item()