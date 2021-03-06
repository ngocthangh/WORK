import scrapy
import json
import csv
import re
from scrapy.shell import inspect_response
from scrapy.http import FormRequest
from dateutil import parser
import time
from datetime import date, timedelta
from langdetect import detect
from scrapy.http import TextResponse
from scrapy.selector import Selector
import time
import langid
from datetime import date, timedelta
from scrapy.loader import ItemLoader
from agoda.items import AgodaReviewItem
from agoda.spiders.queryMySQL import connectMySQL
from agoda.spiders.ConfigurationManager import agodaConfig


class AgodaSpider(scrapy.Spider):
    # REVIEW_PER_PAGE = '50'
    # RATING_OUT_OF = '10'
    # BRANCH = ['Ascott', 'Citadines', 'Somerset']
    # INSERTDB = False
    # LANGUAGE = '[]'
    name = "agodareview"
    allowed_domains = ["agoda.com"]
    start_urls = [
        'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064',
    ]
    handle_httpstatus_list = [503]

    def __init__(self):
        self.Config = agodaConfig()
        self.REVIEW_PER_PAGE = self.Config.REVIEW_PER_PAGE
        self.RATING_OUT_OF = self.Config.RATING_OUT_OF
        self.BRANCH = self.Config.BRANCH
        self.INSERTDB = self.Config.INSERTDB
        self.LANGUAGE = self.Config.LANGUAGE
        self.HEADER = self.Config.HEADER
        self.DATA = self.Config.DATA
        self.HEADER_REVIEW = self.Config.HEADER_REVIEW

        self.css_body_1 = self.Config.css_body_1
        self.css_reviews_1_1 = self.Config.css_reviews_1_1

        self.css_review_id_1_1_1 = self.Config.css_review_id_1_1_1
        self.css_review_info_1_1_2 = self.Config.css_review_info_1_1_2
        self.css_review_detail_1_1_3 = self.Config.css_review_detail_1_1_3

        self.css_review_score_1_1_2_1 = self.Config.css_review_score_1_1_2_1 
        self.css_reviewer_name_1_1_2_2 = self.Config.css_reviewer_name_1_1_2_2 
        self.css_reviewer_nation_1_1_2_3 = self.Config.css_reviewer_nation_1_1_2_3
        self.css_traveler_type_1_1_2_4 = self.Config.css_traveler_type_1_1_2_4
        self.css_room_type_1_1_2_5 = self.Config.css_room_type_1_1_2_5
        self.css_detail_stayed_1_1_2_6 = self.Config.css_detail_stayed_1_1_2_6

        self.css_review_date_1_1_3_1 = self.Config.css_review_date_1_1_3_1
        self.css_review_date_1_1_3_2 = self.Config.css_review_date_1_1_3_2
        self.css_review_title_1_1_3_3 = self.Config.css_review_title_1_1_3_3
        self.css_positive_review_1_1_3_4 = self.Config.css_positive_review_1_1_3_4
        self.css_negative_review_1_1_3_5 = self.Config.css_negative_review_1_1_3_5
        self.css_review_text_1_1_3_6 = self.Config.css_review_text_1_1_3_6

        print(self.REVIEW_PER_PAGE)
        print(self.RATING_OUT_OF)
        for b in self.BRANCH:
            print(b)
        print(self.LANGUAGE)
        print(self.INSERTDB)
        print(self.HEADER)
        print(self.DATA)
        print(self.HEADER_REVIEW)

        if self.INSERTDB:
            self.db = connectMySQL()
            self.db.create_database()
            self.db.create_table()
        self.crawl_till_date = date.today() - timedelta(1)
        self.checkin_date = str(date(date.today().year,12,20)) if date(date.today().year,12,20) > date.today() else str(date(date.today().year,12,20) + timedelta(30))
        self.ids_seen = set()
        self.ids_rev = set()
        self.duplicate = 0
        self.empty_rev = 0
        print(str(self.checkin_date))

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
        with open('citydata/CityFinal_1.csv') as csvfile:
            cities = csv.reader(csvfile, quotechar='"', delimiter=',',
                         quoting=csv.QUOTE_ALL, skipinitialspace=True)
            i = 0
            for city in cities:
                if i == 0 and len(city) > 0:
                    i = 1
                    try:
                       val = int(city[0])
                    except ValueError:
                        continue
                if len(city) > 0:
                    idSearch = str(city[0])
                    header = self.getJson(self.HEADER, '\n', ':')
                    # data0 = "SearchType=1&CityId=%s&PageNumber=1&PageSize=45&SortType=0&CultureInfo=en-US&HasFilter=false&Adults=1&Children=0&Rooms=1&CheckIn=2017-07-29&LengthOfStay=1&ChildAgesStr=" %city[1]
                    data1 =  self.DATA.replace('CityId_Input',idSearch).replace('CheckIn_Input', str(self.checkin_date))
                    formdata = self.getJson(data1, '&', '=')
                    yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', headers = header, formdata = formdata, dont_filter=True, callback=self.parseListHotelPage1, method='POST', meta = {'idSearch': idSearch})
        
    def parseListHotelPage1(self, response):
        # inspect_response(response, self)
        print('###########Searching for id: %s' %response.meta['idSearch'])
        Result = json.loads(response.body)
        totalPage = Result['TotalPage']
        cityName = Result['CityName']
        page = Result['PageNumber']
        TotalFilteredHotels = Result['TotalFilteredHotels']
        cityId = Result['SearchCriteria']['CityId']
        listHotel = Result['ResultList']
        if self.INSERTDB:
            self.db.insert_city(cityId, cityName, 0)
        print('-----------Getting %s hotel' %str(TotalFilteredHotels))
        Check_active = False
        for hotel in listHotel:
            hotelId = hotel['HotelID']
            Name = hotel['EnglishHotelName']
            for branch in self.BRANCH:
                if branch in Name:
                    Check_active = True
                    if hotelId in self.ids_seen:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Duplicate item found: %s" % hotelId)
                        break
                    else:
                        DetailLink = 'https://www.agoda.com' + (hotel['HotelUrl']).split('?')[0]
                        if self.INSERTDB:
                            self.db.insert_hotel(hotelId, Name, DetailLink, self.crawl_till_date)
                        # yield{'hotelId': hotelId}
                        # payload = {"hotelId": str(hotelId),"page":'1', "pageSize":'1',"sorting":'1',"filters":{"language":[],"room":[]}}
                        header = self.getJson(self.HEADER_REVIEW, '\n', ':')
                        body1 = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":'+ self.REVIEW_PER_PAGE +',"sorting":1,"filters":{"language":[],"room":[]}}'
                        yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body1, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'Page': '1'})
                        # body2 = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":'+str(REVIEW_PER_PAGE)+',"sorting":1,"filters":{"language":[2],"room":[]}}'
                        # yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body2, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'Page': '1', 'Lang': 'fr', 'LangBody': '[2]'})
                        # body3 = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":'+str(REVIEW_PER_PAGE)+',"sorting":1,"filters":{"language":[7,8,20],"room":[]}}'
                        # yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body3, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'Page': '1', 'Lang': 'zh', 'LangBody': '[7,8,20]'})
                        self.ids_seen.add(hotelId)
                    break
        if self.INSERTDB and Check_active:
            self.db.update_city(cityId, 1)
        for i in range(2, totalPage + 1):
            header = self.getJson(self.HEADER, '\n', ':')
            data0 = "SearchType=1&CityId=%s&PageNumber=%s&PageSize=45&SortType=0&CultureInfo=en-US&HasFilter=false&Adults=1&Children=0&Rooms=1&CheckIn=2017-07-29&LengthOfStay=1&ChildAgesStr=" %(cityId, i)
            formdata = self.getJson(data0, '&', '=')
            yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', headers = header, formdata = formdata, dont_filter=True, callback=self.parseListHotelPage2, method='POST')
            
                
    def parseListHotelPage2(self, response):
        Result = json.loads(response.body)
        listHotel = Result['ResultList']
        cityId = Result['SearchCriteria']['CityId']
        Check_active = False
        for hotel in listHotel:
            hotelId = hotel['HotelID']
            Name = hotel['EnglishHotelName']
            for branch in self.BRANCH:
                if branch in Name:
                    Check_active = True
                    if hotelId in self.ids_seen:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Duplicate item found: %s" % hotelId)
                        break
                    else:
                        print('######################################### id : Name: %s : %s' %(hotelId, Name))
                        DetailLink = 'https://www.agoda.com' + (hotel['HotelUrl']).split('?')[0]
                        if self.INSERTDB:
                            self.db.insert_hotel(hotelId, Name, DetailLink, self.crawl_till_date)
                        # payload = {"hotelId": str(hotelId),"page":'1',"pageSize":'1',"sorting":'1',"filters":{"language":[],"room":[]}}
                        # yield{'hotelId': hotelId}
                        header = self.getJson(self.HEADER_REVIEW, '\n', ':')
                        body1 = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":'+ self.REVIEW_PER_PAGE +',"sorting":1,"filters":{"language":[],"room":[]}}'
                        yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body1, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'Page': '1'})
                        # body2 = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":'+str(REVIEW_PER_PAGE)+',"sorting":1,"filters":{"language":[2],"room":[]}}'
                        # yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body2, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'Page': '1', 'Lang': 'fr', 'LangBody': '[2]'})
                        # body3 = '{"hotelId":'+str(hotelId)+',"page":1,"pageSize":'+str(REVIEW_PER_PAGE)+',"sorting":1,"filters":{"language":[7,8,20],"room":[]}}'
                        # yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body3, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'Page': '1', 'Lang': 'zh', 'LangBody': '[7,8,20]'})
                        self.ids_seen.add(hotelId)
                    break
        if self.INSERTDB and Check_active:
            self.db.update_city(cityId, 1)
    # def parseCommentNum(self, response):
    #     # inspect_response(response, self)
    #     Bodys = response.css('div#hotelreview-detail-item')
    #     if len(Bodys) > 0:
    #         Body = Bodys[0]
    #         totalReview = 0
    #         for bd in Bodys:
    #             totalRe = bd.css('::attr(data-totalindex)').extract()
    #             if len(totalRe) > 0:
    #                 totalReview = int(totalRe[0])
    #                 if totalReview > 0:
    #                     Body = bd
    #                     break
    #         providerId = Body.css('::attr(data-review-provider)').extract()
    #         if len(providerId) > 0:
    #             providerId = providerId[0]
    #         else:
    #             providerId = ''
    #         hotelId = response.meta['hotelId']
            
    #         print('################# Review Number: %s' %str(totalReview))
    #         pageNumber = int(totalReview / REVIEW_PER_PAGE)
    #         if totalReview % REVIEW_PER_PAGE > 0:
    #             pageNumber += 1
    #         print('################# Page Number: %s' %str(pageNumber))
    #         DetailLink = response.meta['DetailLink']
    #         Name = response.meta['Name']
    #         for i in range(1, pageNumber + 1):
    #             # payload = {"hotelId":str(hotelId),"page":str(i),"pageSize":str(REVIEW_PER_PAGE),"sorting":"1","filters":{"language":[2,7,8,20],"room":[]}}
    #             body = '{"hotelId":'+str(hotelId)+',"page":'+str(i)+',"pageSize":'+str(REVIEW_PER_PAGE)+',"sorting":1,"filters":{"language":' + LANGUAGE + ',"room":[]}}'
    #             header = self.getJson(HEADER_REVIEW, '\n', ':')
    #             yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'page':i, 'DetailLink': DetailLink, 'providerId': providerId, 'Name': Name})
                        
    def parseComment(self, response):
        # inspect_response(response, self)
        Body = response.css(self.css_body_1)
        CheckReviewNum = False
        Reviews = Body.css(self.css_reviews_1_1) 
        for rev in Reviews:
            CheckReviewNum = True
            reId = rev.css(self.css_review_id_1_1_1).extract()
            if len(reId) > 0:
                reId = reId[0]
            else:
                reId = ''

            reInfo = rev.css(self.css_review_info_1_1_2)
            reDetail = rev.css(self.css_review_detail_1_1_3)

            ReviewDate = reDetail.css(self.css_review_date_1_1_3_1).extract()
            if len(ReviewDate) <= 0:
                ReviewDate = reDetail.css(self.css_review_date_1_1_3_2).extract()
            if len(ReviewDate) > 0:
                ReviewDate = ReviewDate[0].strip().split('Reviewed')
                if len(ReviewDate) > 1:
                    ReviewDate = ReviewDate[1].strip()
            else:
                ReviewDate = ''
            parser.parserinfo() 
            dateTimeStamp = parser.parse(ReviewDate)
            ReviewDateParse = date(dateTimeStamp.year, dateTimeStamp.month, dateTimeStamp.day)
            if (ReviewDateParse > self.crawl_till_date):
                continue
            dateTimeStamp = str(time.mktime(dateTimeStamp.timetuple()))


            reScore = reInfo.css(self.css_review_score_1_1_2_1).extract()
            if len(reScore) > 0:
                reScore = reScore[0]
            else:
                reScore = ''

            reviewerName = reInfo.css(self.css_reviewer_name_1_1_2_2).extract()
            if len(reviewerName) > 0:
                reviewerName = reviewerName[0].strip()
            else:
                reviewerName = ''

            reviewerNation = reInfo.css(self.css_reviewer_nation_1_1_2_3).extract()
            if len(reviewerNation) > 1:
                reviewerNation = reviewerNation[1].strip().split('from')
                if len(reviewerNation) > 1:
                    reviewerNation = reviewerNation[1].strip()
                else:
                    reviewerNation = ''
            else:
                reviewerNation = ''

            travelerType = reInfo.css(self.css_traveler_type_1_1_2_4).extract()
            if len(travelerType) > 0:
                travelerType = travelerType[0].strip()
            else:
                travelerType = ''

            roomType = reInfo.css(self.css_room_type_1_1_2_5).extract()
            if len(roomType) > 0:
                roomType = roomType[0].strip()
            else:
                roomType = ''

            detailStayed = reInfo.css(self.css_detail_stayed_1_1_2_6).extract()
            if len(detailStayed) > 0:
                detailStayed = detailStayed[0].strip()
            else:
                detailStayed = ''

            
            ReviewTitle = reDetail.css(self.css_review_title_1_1_3_3).extract()
            if len(ReviewTitle) > 0:
                ReviewTitle = ReviewTitle[0].strip()[:-1]
            else:
                ReviewTitle = ''

            SourceSentiment = ''
            ReviewText = ''
            PositiveReview = ''
            CommentReview = reDetail.css(self.css_positive_review_1_1_3_4).extract()
            if len(CommentReview) > 0:
                PositiveReview = CommentReview[0].strip()
                ReviewText += PositiveReview
                if ReviewText != '':
                    SourceSentiment += 'positive'
            
            NegativeReview = ''
            CommentReview = reDetail.css(self.css_negative_review_1_1_3_5).extract()
            if len(CommentReview) > 0:
                NegativeReview = CommentReview[0].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += NegativeReview
                if NegativeReview != '':
                    if SourceSentiment == '':
                        SourceSentiment += 'negative'
                    else:
                        SourceSentiment = ''

            ReviewText1 = reDetail.css(self.css_review_text_1_1_3_6).extract()
            if len(ReviewText1) > 0:
                ReviewText1 = ReviewText1[0].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += ReviewText1
            else:
                ReviewText1 = ''

            Language = langid.classify(ReviewText)[0]

            hotelId = response.meta['hotelId']
            DetailLink = response.meta['DetailLink']
            Name = response.meta['Name']
            ReviewText = re.sub(r'[\x00-\x1F]+', ' ', ReviewText.replace('\n', '. ').replace('\r', '. ').replace('..', '.').replace('  ', ' '))
            if ReviewText == '' and ReviewTitle == '':
                self.empty_rev += 1
                continue
            rev = reviewerName + reviewerNation + hotelId + dateTimeStamp + reScore + travelerType + roomType + ReviewTitle[:50] + ReviewText[:20] + ReviewText[-20:]
            if rev in self.ids_rev:
                print('Duplicate Review')
                self.duplicate += 1
                continue
            self.ids_rev.add(rev)
            it = ItemLoader(item=AgodaReviewItem())
            it.add_value('title', ReviewTitle)
            it.add_value('comment', ReviewText)
            it.add_value('language', Language)
            it.add_value('date_publish', str(ReviewDateParse))
            it.add_value('date_publish_timestamp', dateTimeStamp)
            it.add_value('product_id', hotelId)
            it.add_value('review_score', reScore)
            it.add_value('rating_out_of', self.RATING_OUT_OF)
            it.add_value('author', reviewerName)
            it.add_value('country', reviewerNation)
            it.add_value('type_of_trip', travelerType)
            it.add_value('room_type', roomType)
            it.add_value('details_stay', detailStayed)
            it.add_value('link', DetailLink)
            it.add_value('data_provider_id', str(self.duplicate) + str(self.empty_rev))
            it.add_value('product_name', Name)
            it.add_value('source_sentiment', SourceSentiment)
            if self.INSERTDB:
                self.db.insert_review(it)
            yield it.load_item()
            
        if (CheckReviewNum):
            Page = int(response.meta['Page'])
            Page += 1
            print('Checking for page %s' %Page)
            body = '{"hotelId":'+str(hotelId)+',"page":'+str(Page)+',"pageSize":'+ self.REVIEW_PER_PAGE + ',"sorting":1,"filters":{"language":[],"room":[]}}'
            header = self.getJson(self.HEADER_REVIEW, '\n', ':')
            yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', body = body, headers = header, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'DetailLink': DetailLink, 'Name': Name, 'Page': Page}) 
        else:
            print('End Page')