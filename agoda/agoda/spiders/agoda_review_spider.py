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



REVIEW_PER_PAGE = 10
HEADER = """Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest"""

class YelpSpider(scrapy.Spider):
    name = "agodareview"
    allowed_domains = ["agoda.com"]
    start_urls = [
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=DK&cid=-1&tag=&gclid=&aid=130243&userId=a45dbc08-94c8-4883-8267-14e589793930&languageId=1&sessionId=fn0s5opvtin15we2ijf5j20s&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2017-07-13&checkOut=2017-08-10&los=28&rooms=1&adults=1&children=0&childages=&ckuid=a45dbc08-94c8-4883-8267-14e589793930',
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=DK&cid=-1&tag=&gclid=&aid=130243&userId=a45dbc08-94c8-4883-8267-14e589793930&languageId=1&sessionId=fn0s5opvtin15we2ijf5j20s&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2018-02-15&checkOut=2018-02-16&los=1&rooms=1&adults=2&children=0&childages=&ckuid=a45dbc08-94c8-4883-8267-14e589793930',
        'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064',
    ]
    handle_httpstatus_list = [503]

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
        with open('test.csv') as csvfile:
            cities = csv.reader(csvfile, quotechar='"', delimiter=',',
                         quoting=csv.QUOTE_ALL, skipinitialspace=True)
            for city in cities:
                header = self.getJson(HEADER, '\n', ':')
                data0 = "SearchType=1&CityId=%s&PageNumber=1&PageSize=45&SortType=0&CultureInfo=en-US&HasFilter=false&Adults=1&Children=0&Rooms=1&CheckIn=2017-07-29&LengthOfStay=1&ChildAgesStr=" %city[1]
                formdata = self.getJson(data0, '&', '=')
                yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', headers = header, formdata = formdata, dont_filter=True, callback=self.parseListHotelPage1, method='POST')
            
    def parseListHotelPage1(self, response):
        # inspect_response(response, self)
        Result = json.loads(response.body)
        totalPage = Result['TotalPage']
        page = Result['PageNumber']
        cityId = Result['SearchCriteria']['CityId']
        listHotel = Result['ResultList']
        for hotel in listHotel:
            hotelId = hotel['HotelID']
            Name = hotel['EnglishHotelName']
            DetailLink = 'https://www.agoda.com/' + slugify(Name) + '/hotel/singapore-sg.html'
            # yield{'hotelId': hotelId}
            payload = {"hotelId": str(hotelId),"page":'1', "pageSize":'10',"sorting":'1',"filters":{"language":[],"room":[]}}
            yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', formdata = payload, dont_filter=True, callback=self.parseCommentNum, method='POST', meta = {'hotelId':str(hotelId),'DetailLink': DetailLink})
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
            print('######################################### id : Name: %s : %s' %(hotelId, Name))
            DetailLink = 'https://www.agoda.com/' + slugify(Name) + '/hotel/singapore-sg.html'
            payload = {"hotelId": str(hotelId),"page":'1',"pageSize":'10',"sorting":'1',"filters":{"language":[],"room":[]}}
            # yield{'hotelId': hotelId}
            yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', formdata = payload, dont_filter=True, callback=self.parseCommentNum, method='POST', meta = {'hotelId':str(hotelId),'DetailLink': DetailLink})
    def parseCommentNum(self, response):
        # inspect_response(response, self)
        Body = response.css('div#hotelreview-detail-item')
        DetailLink = response.meta['DetailLink']
        hotelId = response.meta['hotelId']
        pageText = Body.css('div.review-comments-count span::text').extract()
        print('############# Page: %s' %pageText)
        if len(pageText) > 0: 
            nums = re.findall(r'\d+', ''.join(pageText))
            if len(nums) > 0:
                for i in range(0, len(nums)):
                    if int(nums[i]) > 0:
                        reviewNumber = int(nums[i])
                        print('################# Review Number: %s' %str(reviewNumber))
                        pageNumber = reviewNumber / REVIEW_PER_PAGE
                        if reviewNumber % REVIEW_PER_PAGE > 0:
                            pageNumber += 1
                        print('################# Page Number: %s' %str(pageNumber))
                        for i in range(1, pageNumber + 1):
                            payload = {"hotelId": str(hotelId),"page":str(i),"pageSize":'10',"sorting":'1',"filters":{"language":[],"room":[]}}
                            yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', formdata = payload, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':str(hotelId), 'page':i,'DetailLink': DetailLink})
                        break
    def parseComment(self, response):
        Body = response.css('div#hotelreview-detail-item')

        Reviews = Body.css('div.review-comment-items div.individual-review-item') 
        for re in Reviews:
            reId = re.css('::attr(data-id)').extract()
            if len(reId) > 0:
                reId = reId[0]
            else:
                reId = ''

            reInfo = re.css('div.review-info')

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

            reDetail = re.css('div.nopadding-right div.review-comment-bubble')
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
                ReviewText += 'Positive: ' + PositiveReview
            
            NegativeReview = ''
            if len(CommentReview) > 1:
                NegativeReview = CommentReview[1].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += 'Negative: ' + NegativeReview

            ReviewText1 = reDetail.css('div.comment-text span::text').extract()
            if len(ReviewText1) > 0:
                ReviewText1 = ReviewText1[0].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += 'General: ' + ReviewText1
            else:
                ReviewText1 = ''
            
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
            dateTimeStamp = int(time.mktime(dateTimeStamp.timetuple()))
            Language = ''
            try:
                if(ReviewText != ''):
                    Language = detect(ReviewText)
                pass
            except Exception as e:
                print('Can not detect language!')

            hotelId = response.meta['hotelId']
            yield{
                    'title': ReviewTitle,
                    'text': ReviewText,
                    'detect language': Language,
                    'date publish': ReviewDate,
                    'timestamp': dateTimeStamp,
                    'product id': hotelId,
                    'review score': reScore,
                    'author': reviewerName,
                    'country': reviewerNation,
                    'tags': travelerType,
                    'Room Type Used': roomType,
                    'Detail Stayed': detailStayed,
                    'product link': response.meta['DetailLink'],
                }