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
        def getJson(data, deli, center):
            data1 = data.split(deli)
            data = '{ '
            for d in data1:
                if len(d.split(center)) > 1:
                    data += '\"' + d.split(center)[0].strip() + '\":\"' + d.split(center)[1].strip() + '\"' + ','
                else:
                    data += '\"' + d.split(center)[0].strip() + '\":\"\"' + ','
            data = data[:-1] + ' }'
            return json.loads(data)
        # hotelId = 1411720
        # hotelId = 400658
        # payload = {"hotelId": str(hotelId),"providerId":'332',"demographicId":'0',"page":'27',"pageSize":'10',"sorting":'1',"providerIds":'332',"isReviewPage":'false',"isCrawlablePage":'true',"filters":{"language":[],"room":[]}}
        # yield FormRequest('https://www.agoda.com/NewSite/en-us/Review/ReviewComments', formdata = payload, callback=self.parseCommentNum, method='POST', meta = {'hotelId':hotelId})
        cookie0 = 'agoda.user.03=UserId=62ce4cfa-32e7-45ba-aa93-cd10a5f1a9fc; agoda.prius=PriusID=0&PointsMaxTraffic=Agoda; agoda.lastclicks=-1||||2017-07-11T17:57:29||lvpgdvioc3wldu0db0dgqjuc||{"IsPaid":false,"gclid":"","Type":""}; _ab50group=GroupB; _40-40-20Split=Group40B; mousestats_vi=dfcf8d4da299212cd519; kampyle_userid=fbde-a66c-38ac-c00c-7585-6a4a-4563-2ecb; cd_user_id=15d314972e21-05432146c0c124-57112011-100200-15d314972e37c; agoda.customer=VdCmts=73753045$1; agodalbhkg=www.agoda.com_cluster_2b; ASP.NET_SessionId=pepv2r5y0ktrbrp02km3urkw; agoda.firstclicks=-1||||2017-07-19T21:33:20||pepv2r5y0ktrbrp02km3urkw||{"IsPaid":false,"gclid":"","Type":""}; ak_bmsc=A7F230DDEB1754C9174E6FE13EFCEF4917C966B4DB180000B06D6F5915B5171E~plbDlLLZhG46NtVXKO170dJsncQ8JPyPRNjSoH/gY0ndCbAar6dWga7w+/XBMYyZawjw+0cDI4OKJVImmjK6oa1OGPzZ/528anW74Senpm5WvGtDKCJc4SCSOFKyi65cW0tOTIZUvkjInhStL+ulTOn68Abvo1KayptU16XSu3ZbqpENGkoM0J8+qutxPxcnxzwG3CBMTZXQ+ZWefmt2DWeEkF4JwBr1XCgueGEzaGI3Q=; AMCVS_914D3A93584ED0070A495DB9%40AdobeOrg=1; AMCV_914D3A93584ED0070A495DB9%40AdobeOrg=2096510701%7CMCIDTS%7C17367%7CMCMID%7C42325389378055286591355038603775929246%7CMCOPTOUT-1500481837s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C2.0.0; s_vnum=1500483600638%26vn%3D1; s_vmonthnum=1501520400254%26vn%3D9; ABSTATIC=1; backendDataInSessionFlag=false; kampyleUserSession=1500476495566; kampyleUserSessionsCount=5; agoda.attr.03=CookieId=fd024649-7ec4-458d-8478-faa9deabc900&ATItems=-1$07-19-2017 22:04$; agoda.allclicks=-1||||2017-07-19T22:04:29||pepv2r5y0ktrbrp02km3urkw||{"IsPaid":false,"gclid":"","Type":"LC"}; agoda.search.01=SHist=1$4064$6071$1$1$2$0$0$$|1$4064$6071$1$1$1$0$0$$|1$4064$6071$1$1$1$0$0$$|4$522662$6071$1$1$1$0$0$$|1$4064$6046$1$1$1$0$0$$|4$400658$6046$1$1$1$0$0$$|4$522662$6046$1$1$1$0$0$$|1$4064$6046$1$1$1$0$0$$|1$4064$6046$1$1$1$0$0$$|1$13170$6046$1$1$1$0$0$$; s_cc=true; utag_main=v_id:015d314963fc0008e4f7c57b7d1f05087001c07f0086e$_sn:5$_ss:0$_st:1500478308794$_pn:4%3Bexp-session$ses_id:1500474638744%3Bexp-session; agoda.version.03=CookieId=3d6cc67d-cd6f-4920-8611-3b2e3914edf8&AllocId=3de252aebd5fafedf1a03c8af66877add41e7425075cb0f85fdc4cc2a0a15d032b65e7202c51f7f9fa36a28e21a4ae3009f228203f7b7c3f362b0cc962c1a0d804225f553a49d5dcb26a181eb8b51845d30d5fe9f33d6cc67dcd6f9206113b2e3914edf8&DPN=1&DLang=vi-vn&CurLabel=XCD&Alloc=953$16|2069$52|2071$76|2079$25|2221$8|2188$69|2192$10|2211$83|2201$14|2273$4|2291$58|2346$59|2226$86|2229$82|2288$65|2308$45|2333$27|2528$53&FEBuildVersion=&CurIP=&TItems=2$-1$07-13-2017 18:26$07-13-2018 18:26$&CuCur=79; s_ptc=0.00%5E%5E0.00%5E%5E0.00%5E%5E0.00%5E%5E0.61%5E%5E0.43%5E%5E3.20%5E%5E1.21%5E%5E5.05; _ga=GA1.2.624899625.1499770481; _gid=GA1.2.1081404954.1500474640; kampyleSessionPageCounter=2; s_getNewRepeat=1500476533885-Repeat; s_sq=acpltdagodacomlive%3D%2526c.%2526a.%2526activitymap.%2526page%253Dagoda%25257Cvi-vn%25257Cnewssr%25257Ckh%252526%252523225%25253Bch%252520s%2525E1%2525BA%2525A1n%252520%2525E1%2525BB%25259F%252520h%2525E1%2525BB%252593%252520ch%252526%252523237%25253B%252520minh%2526link%253DTrang%252520k%2525E1%2525BA%2525BF%2526region%253DpaginationContainer%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dagoda%25257Cvi-vn%25257Cnewssr%25257Ckh%252526%252523225%25253Bch%252520s%2525E1%2525BA%2525A1n%252520%2525E1%2525BB%25259F%252520h%2525E1%2525BB%252593%252520ch%252526%252523237%25253B%252520minh%2526pidt%253D1%2526oid%253DTrang%252520k%2525E1%2525BA%2525BF%2526oidt%253D3%2526ot%253DSUBMIT; session_cache={"Cache":"HK3","Time":"636360735006906336","SessionID":"pepv2r5y0ktrbrp02km3urkw","CheckID":"4d6170e5301f5f81779e5b7bdc9a6ee184a3a4be","CType":"N"}; s_ppvl=agoda%257Cvi-vn%257Cnewssr%257Ckh%2526%2523225%253Bch%2520s%25u1EA1n%2520%25u1EDF%2520h%25u1ED3%2520ch%2526%2523237%253B%2520minh%2C2%2C2%2C236%2C1366%2C236%2C1366%2C768%2C1%2CP; s_ppv=agoda%257Cvi-vn%257Cnewssr%257Ckh%2526%2523225%253Bch%2520s%25u1EA1n%2520%25u1EDF%2520singapore%2C1%2C1%2C150%2C1366%2C150%2C1366%2C768%2C1%2CP'
        # cookie = getJson(cookie0, ';', '=')
        header0 = """Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest"""
        header = getJson(header0, '\n', ':')
        print(header)
        data0 = """SearchMessageID=393f6a29-f8a6-4207-aeb5-e689d0fe6a8f
IsPollDmc=false
SearchType=1
ObjectID=0
Filters[HotelName]
Filters[PriceRange][Min]=0
Filters[PriceRange][Max]=0
Filters[PriceRange][IsHavePriceFilterQueryParamter]=false
Filters[ReviewScoreMin]=0
Filters[Size]=0
RateplanIDs
TotalHotels=373
PlatformID=1001
CurrentDate=2017-07-19T23:22:41.7170328+07:00
SearchID=991110719232241700
CityId=4064
Latitude=0
Longitude=0
Radius=0
RectangleSearchParams
PageNumber=3
PageSize=45
SortType=0
IsSortChanged=false
SortByAsd=false
ReviewTravelerType=0
PointsMaxProgramId=0
PollTimes=1
MaxPollTimes=0
CityName=Singapore
ObjectName=Singapore
AddressName
CountryName=Singapore
CountryId=114
IsAllowYesterdaySearch=false
CultureInfo=en-US
UnavailableHotelId=0
IsEnableAPS=false
AdditionalExperiments[PRIUS]=1008617
SeletedHotelId=0
HasFilter=false
LandingParameters[HeaderBannerUrl]
LandingParameters[FooterBannerUrl]
LandingParameters[SelectedHotelId]=0
LandingParameters[LandingCityID]=0
NewSSRSearchType=1
IsWysiwyp=false
RequestPriceView
FinalPriceView=1
MapType=1
IsShowMobileAppPrice=false
IsApsPeek=false
IsRetailPeek=false
IsRetina=false
CheckInCultureDateText=28/07/2017
CheckOutCultureDateText=29/07/2017
IsCriteriaDatesChanged=false
TotalHotelsFormatted=373
PreviewRoomFinalPrice
ReferrerUrl
CountryEnglishName=Singapore
CityEnglishName=Singapore
Adults=1
Children=0
Rooms=1
CheckIn=2017-07-28T23:22:41.7170328+07:00
LengthOfStay=1
ChildAgesStr
Text=Singapore
ExtraText
IsDateless=false"""
        formdata = getJson(data0, '\n', '=')
        print(formdata)
        body = 'SearchMessageID=8f7d6503-4b6d-4819-af3d-f23c8c07162b&IsPollDmc=false&SearchType=1&ObjectID=0&Filters%5BHotelName%5D=&Filters%5BPriceRange%5D%5BMin%5D=0&Filters%5BPriceRange%5D%5BMax%5D=0&Filters%5BPriceRange%5D%5BIsHavePriceFilterQueryParamter%5D=false&Filters%5BReviewScoreMin%5D=0&Filters%5BSize%5D=0&RateplanIDs=&TotalHotels=372&PlatformID=1001&CurrentDate=2017-07-19T22%3A54%3A11.1041246%2B07%3A00&SearchID=991110719225411100&CityId=4064&Latitude=0&Longitude=0&Radius=0&RectangleSearchParams=&PageNumber=2&PageSize=45&SortType=0&IsSortChanged=false&SortByAsd=false&ReviewTravelerType=0&PointsMaxProgramId=0&PollTimes=0&MaxPollTimes=0&CityName=Singapore&ObjectName=Singapore&AddressName=&CountryName=Singapore&CountryId=114&IsAllowYesterdaySearch=false&CultureInfo=vi-VN&UnavailableHotelId=0&IsEnableAPS=false&AdditionalExperiments%5BPRIUS%5D=1008617&SeletedHotelId=0&HasFilter=false&LandingParameters%5BHeaderBannerUrl%5D=&LandingParameters%5BFooterBannerUrl%5D=&LandingParameters%5BSelectedHotelId%5D=0&LandingParameters%5BLandingCityID%5D=0&NewSSRSearchType=0&IsWysiwyp=false&RequestPriceView=&FinalPriceView=1&MapType=1&IsShowMobileAppPrice=false&IsApsPeek=false&IsRetailPeek=false&IsRetina=false&CheckInCultureDateText=28%2F07%2F2017&CheckOutCultureDateText=29%2F07%2F2017&IsCriteriaDatesChanged=false&TotalHotelsFormatted=372&PreviewRoomFinalPrice=&ReferrerUrl=&CountryEnglishName=Singapore&CityEnglishName=Singapore&Adults=1&Children=0&Rooms=1&CheckIn=2017-07-28T22%3A54%3A11.1041246%2B07%3A00&LengthOfStay=1&ChildAgesStr=&Text=Singapore&ExtraText=&IsDateless=false'
        yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', headers = header, body = body, callback=self.parseCommentNum, method='POST')

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
        #             for i in range(1, int(pageNumber) + 1):
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

            ReviewText = reDetail.css('div.comment-text span::text').extract()
            if len(ReviewText) <= 0: 
                ReviewText = reDetail.css('div.comment-icon span::text').extract()
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
                    'Review Title': ReviewTitle,
                    'Text': ReviewText,
                    'Language': Language,
                    'Date': ReviewDate,
                    'Date Timestamp': dateTimeStamp,
                    'ProductId': hotelId,
                    'Review Score': reScore,
                    'Reviewer Name': reviewerName,
                    'Reviewer Nation': reviewerNation,
                    'Traveler Type': travelerType,
                    'Room Type Used': roomType,
                    'Detail Stayed': detailStayed,
                }