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
# from selenium import webdriver
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# from pyvirtualdisplay import Display

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
    
    # def __init__(self):
        # capabilities = webdriver.DesiredCapabilities().FIREFOX
        # capabilities["marionette"] = False
        # binary = FirefoxBinary(r'C:\Python34\selenium\webdriver\firefox\amd64\geckodriver.exe')
        # self.driver = webdriver.Remote("http://127.0.0.1:4444", capabilities)
        # self.driver = webdriver.Chrome()
        # self.driver.get('http://www.google.com')
        # binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
        # browser = webdriver.Firefox(firefox_binary=binary)

    def parse(self, response):
        # hotelId = 254056
        # hotelId = 109878
        # parseListHotel(response)
        # self.driver.get(response.request.url)
        # self.driver.implicitly_wait(5)

        # while True:
        #     next = self.driver.find_element_by_css('button#paginationNext')
        #     try:
        #         next.click()
        #         # get the data and write it to scrapy items
        #         parseListHotel(response)
        #     except:
        #         break
        # self.driver.close()

        payload = {
"SearchMessageID":"bb55721a-02be-4c8f-bfa8-e9b1cd959bff",
"IsPollDmc":"false",
"SearchType":"1",
"ObjectID":"0",
"Filters[HotelName]":"",
"Filters[PriceRange][Min]":"0",
"Filters[PriceRange][Max]":"0",
"Filters[PriceRange][IsHavePriceFilterQueryParamter]":"false",
"Filters[ReviewScoreMin]":"5",
"Filters[Size]":"0",
"RateplanIDs":"",
"TotalHotels":"411",
"PlatformID":"1001",
"CurrentDate":"2017-07-13T08:01:03.0146706+07:00",
"SearchID":"991110713080103000",
"CityId":"4064",
"Latitude":"0",
"Longitude":"0",
"Radius":"0",
"RectangleSearchParams":"",
"PageNumber":"2",
"PageSize":"45",
"SortType":"0",
"IsSortChanged":"false",
"SortByAsd":"false",
"ReviewTravelerType":"0",
"PointsMaxProgramId":"0",
"PollTimes":"0",
"MaxPollTimes":"0",
"CityName":"Singapore",
"ObjectName":"Singapore",
"AddressName":"",
"CountryName":"Singapore",
"CountryId":"114",
"IsAllowYesterdaySearch":"false",
"CultureInfo":"en-US",
"UnavailableHotelId":"0",
"IsEnableAPS":"false",
"AdditionalExperiments[PRIUS]":"1008617",
"SeletedHotelId":"0",
"HasFilter":"false",
"LandingParameters[HeaderBannerUrl]":"",
"LandingParameters[FooterBannerUrl]":"",
"LandingParameters[SelectedHotelId]":"0",
"LandingParameters[LandingCityID]":"0",
"NewSSRSearchType":"0",
"IsWysiwyp":"false",
"RequestPriceView":"",
"FinalPriceView":"1",
"MapType":"1",
"IsShowMobileAppPrice":"false",
"IsApsPeek":"false",
"IsRetailPeek":"false",
"IsRetina":"false",
"CheckInCultureDateText":"7/21/2017",
"CheckOutCultureDateText":"7/22/2017",
"IsCriteriaDatesChanged":"false",
"TotalHotelsFormatted":"411",
"PreviewRoomFinalPrice":"",
"ReferrerUrl":"",
"CountryEnglishName":"Singapore",
"CityEnglishName":"Singapore",
"Adults":"1",
"Children":"0",
"Rooms":"1",
"CheckIn":"2017-07-21T00:00:00",
"LengthOfStay":"1",
"ChildAgesStr":"",
"Text":"Singapore",
"ExtraText":"",
"IsDateless":"false",
}
        header = {'content-type':'application/json'}
        yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', formdata = payload, headers = header, callback=self.parseCommentNum, method='POST')
    
    def parseListHotel(response):
        inspect_response(response, self)
        # HOTELS = response.css('ol#hotelListContainer')
        # Hotels = HOTELS.css('li[data-selenium="hotel-item"]')
        # for hotel in Hotels:
        #     hotelId = hotel.css('::attr(data-hotelid)').extract()
        #     if len(hotelId) > 0:
        #         hotelId = hotelId[0].strip()
        #         payload = {"hotelId": str(hotelId),"page":'1',"sorting":'1',"isReviewPage":'false',"isCrawlablePage":'true',"filters":{"language":[],"room":[]}}
        #         yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', formdata = payload, callback=self.parseCommentNum, method='POST', meta = {'hotelId':hotelId})
            

    def parseCommentNum(self, response):
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        inspect_response(response, self)
        # Body = response.css('div#hotelreview-detail-item')
        # hotelId = response.meta['hotelId']
        # pageText = Body.css('div.review-comments-count span::text').extract()
        # print('############# Page: %s' %pageText)
        # if len(pageText) > 0: 
        #     text = pageText[0].split('Showing')
        #     if len(text) > 1:
        #         text1 = text[1].split('verified')
        #         if len(text1) > 0:
        #             result = text1[0].strip()
        #             reviewNumber = int(result)
        #             print('################# Review Number: %s' %str(reviewNumber))
        #             pageNumber = reviewNumber / REVIEW_PER_PAGE
        #             if reviewNumber % REVIEW_PER_PAGE > 0:
        #                 pageNumber += 1
        #             print('################# Page Number: %s' %str(pageNumber))
        #             for i in range(1, pageNumber + 1):
        #                 # if i > 3:
        #                 #     break
        #                 payload = {"hotelId": str(hotelId),"page":str(i),"sorting":'1',"isReviewPage":'false',"isCrawlablePage":'true',"filters":{"language":[],"room":[]}}
        #                 yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', formdata = payload, callback=self.parseComment, method='POST', dont_filter=True, meta = {'hotelId':hotelId, 'page':i})
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
            PositiveReview = reDetail.css('div.comment-icon span::text').extract()
            if len(PositiveReview) > 0:
                PositiveReview = PositiveReview[0].strip()
                ReviewText += 'Positive: ' + PositiveReview
            else:
                PositiveReview = ''

            ReviewText1 = reDetail.css('div.comment-text span::text').extract()
            if len(ReviewText1) > 0:
                ReviewText1 = ReviewText1[0].strip()
                if ReviewText != '':
                    ReviewText += '\n'
                ReviewText += ReviewText1
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
                }