import scrapy
import json
import csv
import re
from slugify import slugify
# from scrapy.shell import inspect_response
from scrapy.http import FormRequest
from dateutil import parser
import time
from datetime import date, timedelta
import langid
from scrapy.http import TextResponse
from scrapy.selector import Selector
import time
from scrapy.loader import ItemLoader
from agoda.items import CtripItem

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
class CtripIncrementSpider(scrapy.Spider):
    name = "ctripincrement"
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
            hotelId = hotel[0]
            Name = hotel[1]
            DetailLink = hotel[2]
            DateCrawled = hotel[3]
            if(DateCrawled == self.crawl_till_date):
                continue
            print('###########Incrementing for hotel Id: %s from date %s to %s' %(hotelId, str(DateCrawled), self.crawl_till_date))
            data = "hotelid=%s&PageNo=%s&ReviewType=All&IsImageOnly=false&IsContentOnly=1&IsRecommend=false&ThemeVBId=0&BaseRoomType=&SelectedLabel=4" %(hotelId, i)
            formdata = self.getJson(data, '&', '=')
            header = self.getJson(HEADER, '\n', ':')
            yield FormRequest('http://english.ctrip.com/hotels/Detail/GetReviewListHtmlV2', headers = header, formdata = formdata, dont_filter=True, callback=self.parseComment, method='POST',meta = {'hotelId':str(hotelId),'DetailLink':DetailLink, 'Name': Name, 'Page': '1'}) 
            self.ids_seen.add(hotelId)
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
        CheckReviewNum = False
        for review in reviewItems:
            CheckReviewNum = True
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
            Langid_text = ''
            Langdetect_text = ''
            try:
                if(ReviewText != ''):
                    Lang_langid = self.identifier.classify(ReviewText)
                    Langid_text = str(Lang_langid)
                    Lang_langdetects = detect_langs(ReviewText)
                    Langdetect_text = str(Lang_langdetects)
                    langid = Lang_langid[0]
                    langdetect_first = str(Lang_langdetects[0]).split(':')[0].replace('zh-cn','zh').replace('zh-tw','zh')
                    langid_pro = float(Lang_langid[1])
                    langdetect_first_pro = float(str(Lang_langdetects[0]).split(':')[1])
                    langdetects =[]
                    langdetects1 =[]
                    for lang in Lang_langdetects:
                        langdetects1.append(str(str(lang).split(':')[0]).replace('zh-cn','zh').replace('zh-tw','zh'))
                        langdetects.append([str(str(lang).split(':')[0]).replace('zh-cn','zh').replace('zh-tw','zh'),float(str(lang).split(':')[1])])
                    langdetects.append([langid,langid_pro])
                    langdetects1.append(langid)
                    if(langid == langdetect_first):
                        if (langid_pro > 0.9 and langdetect_first_pro > 0.9):
                            Language = langid
                        else:
                            for lang in langdetects:
                                if (lang[0] == 'en' and lang[1] > 0.5):
                                    Language = 'en'
                                break
                            if (Language == ''):
                                Language = langid
                    elif ('en' in langdetects1 and 'zh' in langdetects1):
                        Language = 'zh'
                    else:
                        for lang in langdetects:
                            if (lang[0] == 'en' and lang[1] > 0.5):
                                Language = 'en'
                                break
                        if (Language == ''):
                            if ('zh' in langdetects1 and 'ko' in langdetects1):
                                Language = 'zh'
                            elif ('ja' in langdetects1 and 'zh' in langdetects1):
                                Language = 'zh'
                            elif (langid_pro >= langdetect_first_pro):
                                Language = langid
                            else:
                                Language = langdetect_first
                pass
            except Exception as e:
                print('Can not detect language! %s' + str(e))
            if Language not in LANGUAGE:
                continue

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
        if(CheckReviewNum):
            Page = int(response.meta['Page'])
            Page += 1
            data = "hotelid=%s&PageNo=%s&ReviewType=All&IsImageOnly=false&IsContentOnly=1&IsRecommend=false&ThemeVBId=0&BaseRoomType=&SelectedLabel=4" %(hotelId, i)
            formdata = self.getJson(data, '&', '=')
            header = self.getJson(HEADER, '\n', ':')
            yield FormRequest('http://english.ctrip.com/hotels/Detail/GetReviewListHtmlV2', headers = header, formdata = formdata, dont_filter=True, callback=self.parseComment, method='POST',meta = {'hotelId':str(hotelId),'DetailLink':DetailLink, 'Name': Name, 'Page': Page}) 