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
RATING_OUT_OF = '10'
BRANCH = ['Ascott', 'Citadines', 'Somerset']
# BRANCH = ['Snow Lavender']
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
class AgodaSpider(scrapy.Spider):
    name = "agodaincrement"
    allowed_domains = ["agoda.com"]
    start_urls = [
        'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064',
    ]
    handle_httpstatus_list = [503]

    def __init__(self):
        self.db = connectMySQL()
        self.db.selectDB()
        self.crawl_till_date = date.today() - timedelta(1)
        self.ids_seen = set()
        self.ids_rev = set()
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
        # inspect_response(response, self)
        ListHotels = self.db.query_hotel()
        i = 0
        for hotel in ListHotels:
            # i += 1
            # if i < 3:
            #     continue
            # if i > 3:
            #     break
            hotelId = (hotel[0])
            Name = (hotel[1])
            DetailLink = (hotel[2])
            DateCrawled = (hotel[3])
            if(DateCrawled == self.crawl_till_date):
                continue
            print('###########Incrementing for hotel Id: %s from date %s to %s' %(hotelId, str(DateCrawled), self.crawl_till_date))
            body = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":'+str(REVIEW_PER_PAGE)+',"sorting":1,"filters":{"language":' + LANGUAGE + ',"room":[]}}'
            header = self.getJson(HEADER_REVIEW, '\n', ':')
            yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'DateCrawled': str(DateCrawled), 'Page': '1'})  
            self.ids_seen.add(hotelId)
    
    def parseComment(self, response):
        # inspect_response(response, self)
        hotelId = response.meta['hotelId']
        DetailLink = response.meta['DetailLink']
        # providerId = response.meta['providerId']
        Name = response.meta['Name']
        DateCrawled = response.meta['DateCrawled']
        print(Name)
        Body = response.css('div#hotelreview-detail-item')
        Reviews = Body.css('div.review-comment-items div.individual-review-item') 
        CheckDate = False
        CheckNumReview = False
        for re in Reviews:
            CheckNumReview = True
            reId = re.css('::attr(data-id)').extract()
            if len(reId) > 0:
                reId = reId[0]
            else:
                reId = ''

            reInfo = re.css('div.review-info')
            reDetail = re.css('div.nopadding-right div.review-comment-bubble')

            dateCrawledParsed = parser.parse(DateCrawled)
            dateCrawledParsed = date(dateCrawledParsed.year, dateCrawledParsed.month, dateCrawledParsed.day)
            ReviewDate = reDetail.css('div.comment-date-only div.comment-date span::text').extract()
            if len(ReviewDate) <= 0:
                ReviewDate = reDetail.css('div.comment-date-translate div.comment-date span::text').extract()
            if len(ReviewDate) > 0:
                ReviewDate = ReviewDate[0].strip().split('Reviewed')
                if len(ReviewDate) > 1:
                    ReviewDate = ReviewDate[1].strip()
            else:
                ReviewDate = ''
            parser.parserinfo() 
            dateTimeStamp = parser.parse(ReviewDate)
            ReviewDateParse = date(dateTimeStamp.year, dateTimeStamp.month, dateTimeStamp.day)
            
            if(ReviewDateParse <= dateCrawledParsed):
                print('All Crawled')
                continue
            CheckDate = True
            if (ReviewDateParse > self.crawl_till_date):
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
                ReviewText += PositiveReview
            
            NegativeReview = ''
            if len(CommentReview) > 1:
                NegativeReview = CommentReview[1].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += NegativeReview

            ReviewText1 = reDetail.css('div.comment-text span::text').extract()
            if len(ReviewText1) > 0:
                ReviewText1 = ReviewText1[0].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += ReviewText1
            else:
                ReviewText1 = ''
            
            Language = ''
            try:
                if(ReviewText != ''):
                    Language = detect(PositiveReview + NegativeReview + ReviewText1)
                    if Language == 'ko':
                        Language = 'zh-tw'
                pass
            except Exception as e:
                print('Can not detect language!')

            rev = reviewerName + reviewerNation + hotelId + dateTimeStamp + reScore + ReviewTitle
            if rev in self.ids_rev:
                print('Duplicate Review for: %s' %rev)
                continue
            it = ItemLoader(item=AgodaReviewItem())
            it.add_value('title', ReviewTitle)
            it.add_value('text', ReviewText)
            it.add_value('detected_lang', Language)
            it.add_value('published_date_1', str(ReviewDateParse))
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
            # it.add_value('data_provider_id', providerId)
            it.add_value('product_name', Name)
            # self.db.insert_review(it)
            yield it.load_item()
            self.ids_rev.add(rev)
        if CheckNumReview:
            Page = int(response.meta['Page'])
            Page += 1
            print('Checking for page %s' %Page)
            body = '{"hotelId":'+str(hotelId)+',"page":'+str(Page)+',"pageSize":'+str(REVIEW_PER_PAGE)+',"sorting":1,"filters":{"language":' + LANGUAGE + ',"room":[]}}'
            header = self.getJson(HEADER_REVIEW, '\n', ':')
            yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'DateCrawled': str(DateCrawled), 'Page': Page})  
        else:
            print('End Page')