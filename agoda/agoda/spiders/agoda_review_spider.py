import scrapy
import json
from msvcrt import getch
import csv
import re
from slugify import slugify
from scrapy.shell import inspect_response
from scrapy.http import FormRequest

REVIEW_PER_PAGE = 10

class YelpSpider(scrapy.Spider):
    name = "agodareview"
    allowed_domains = ["agoda.com"]
    start_urls = [
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=DK&cid=-1&tag=&gclid=&aid=130243&userId=a45dbc08-94c8-4883-8267-14e589793930&languageId=1&sessionId=fn0s5opvtin15we2ijf5j20s&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2017-07-13&checkOut=2017-08-10&los=28&rooms=1&adults=1&children=0&childages=&ckuid=a45dbc08-94c8-4883-8267-14e589793930',
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=DK&cid=-1&tag=&gclid=&aid=130243&userId=a45dbc08-94c8-4883-8267-14e589793930&languageId=1&sessionId=fn0s5opvtin15we2ijf5j20s&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2018-02-15&checkOut=2018-02-16&los=1&rooms=1&adults=2&children=0&childages=&ckuid=a45dbc08-94c8-4883-8267-14e589793930',
        'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064',
    ]
    handle_httpstatus_list = [503]
        
    def parse(self, response):
        hotelId = 1411720
        payload = {"hotelId": str(hotelId),"page":'39',"sorting":'1',"isReviewPage":'false',"isCrawlablePage":'true',"filters":{"language":[],"room":[]}}
        yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', formdata = payload, callback=self.parseCommentNum, method='POST', meta = {'hotelId':hotelId})
    def parseCommentNum(self, response):
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        # inspect_response(response, self)
        Body = response.css('div#hotelreview-detail-item')
        hotelId = response.meta['hotelId']
        pageText = Body.css('div.review-comments-count span::text').extract()
        print('############# Page: %s' %pageText)
        if len(pageText) > 0: 
            text = pageText[0].split('Showing')
            if len(text) > 1:
                text1 = text[1].split('verified')
                if len(text1) > 0:
                    result = text1[0].strip()
                    reviewNumber = int(result)
                    print('################# Review Number: %s' %str(reviewNumber))
                    pageNumber = reviewNumber / REVIEW_PER_PAGE
                    if reviewNumber % REVIEW_PER_PAGE > 0:
                        pageNumber += 1
                    print('################# Page Number: %s' %str(pageNumber))
                    for i in range(1, pageNumber + 1):
                        # if i > 3:
                        #     break
                        payload = {"hotelId": str(hotelId),"page":str(i),"sorting":'1',"isReviewPage":'false',"isCrawlablePage":'true',"filters":{"language":[],"room":[]}}
                        yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', formdata = payload, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':hotelId, 'page':i})
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

            ReviewText = reDetail.css('div.comment-text span::text').extract()
            if len(ReviewText) > 0:
                ReviewText = ReviewText[0].strip()
            else:
                ReviewText = ''

            ReviewDate = reDetail.css('div.comment-date-only div.comment-date span::text').extract()
            if len(ReviewDate) <= 0:
                ReviewDate = reDetail.css('div.comment-date-translate div.comment-date span::text').extract()
            if len(ReviewDate) > 0:
                ReviewDate = ReviewDate[0].strip().split('Reviewed')
                if len(ReviewDate) > 1:
                    ReviewDate = ReviewDate[1].strip()
            else:
                ReviewDate = ''

            hotelId = response.meta['hotelId']
            yield{
                    'Review Title': ReviewTitle,
                    'Text': ReviewText,
                    'Date': ReviewDate,
                    'ProductId': hotelId,
                    'Review Score': reScore,
                    'Reviewer Name': reviewerName,
                    'Reviewer Nation': reviewerNation,
                    'Traveler Type': travelerType,
                    'Room Type Used': roomType,
                    'Detail Stayed': detailStayed,
                    'Page': response.meta['page'],
                }