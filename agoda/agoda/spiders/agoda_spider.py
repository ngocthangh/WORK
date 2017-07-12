import scrapy
import json
from msvcrt import getch
import csv
import re
from slugify import slugify
from scrapy.shell import inspect_response
from scrapy.http import FormRequest

class YelpSpider(scrapy.Spider):
    name = "agoda"
    allowed_domains = ["agoda.com"]
    start_urls = [
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=DK&cid=-1&tag=&gclid=&aid=130243&userId=a45dbc08-94c8-4883-8267-14e589793930&languageId=1&sessionId=fn0s5opvtin15we2ijf5j20s&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2017-07-13&checkOut=2017-08-10&los=28&rooms=1&adults=1&children=0&childages=&ckuid=a45dbc08-94c8-4883-8267-14e589793930',
        # 'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064&pagetypeid=103&origin=DK&cid=-1&tag=&gclid=&aid=130243&userId=a45dbc08-94c8-4883-8267-14e589793930&languageId=1&sessionId=fn0s5opvtin15we2ijf5j20s&storefrontId=3&currencyCode=DKK&htmlLanguage=en-us&trafficType=User&cultureInfoName=en-US&checkIn=2018-02-15&checkOut=2018-02-16&los=1&rooms=1&adults=2&children=0&childages=&ckuid=a45dbc08-94c8-4883-8267-14e589793930',
        'https://www.agoda.com/pages/agoda/default/DestinationSearchResult.aspx?city=4064',

    ]
    handle_httpstatus_list = [503]
    # def parse(self, response):
    #     cr = csv.reader(open(r"D:\Yelp\SVN\trunk\Project\tutorial_Tu\tutorial\spiders\us_postal_codes_revert.csv","r"))
    #     for row in cr:
    #         while (row[0][0] == '0'):
    #             row[0] = row[0][+1:]
    #         print('$$$$$$$$$$$$$$$$$$$$$$$$$ search: %s $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$' %row[0])
    #         yelp_url  = "https://www.yelp.com/search?cflt=restaurants&find_loc=%s" % row[0].strip()
    #         print(yelp_url)
    #         yield response.follow(yelp_url, self.parseSearchPage)
        
    def parse(self, response):
        # def slugify(text):
        #     text = unidecode.unidecode(text).lower()
        #     return re.sub(r'\W+', '-', text)
        HOTELS = response.css('ol#hotelListContainer')
        Hotels = HOTELS.css('li[data-selenium="hotel-item"]')
        for hotel in Hotels:
            MediaBox = hotel.css('div.media-box')
            PriceContainer = hotel.css('div.hotel-price-promo-container')
            HotelInfo = hotel.css('div.hotel-info')

            transports = []
            Transport = MediaBox.css('figure.ssr-media div.transport-badge-container::attr(title)').extract()
            if len(Transport) > 0:
                Transport = Transport[0].split('</span>')
                for i in range(0, len(Transport)):
                    if i == len(Transport) - 1:
                        break
                    items = Transport[i].split('>')
                    item = items[len(items) - 1]
                    transports.append(item)


            YearAwarded = HotelInfo.css('ul.property-info-container li span[data-selenium="hotel-gca"] span.badge-gca-year::text').extract()
            if len(YearAwarded) > 0:
                YearAwarded = YearAwarded[0].strip()
            else:
                YearAwarded = ''

            Name = HotelInfo.css('ul.property-info-container li h3.hotel-name::text').extract()
            if len(Name) > 0:
                Name = Name[0].strip()
            else:
                Name = ''

            Rating = HotelInfo.css('ul.property-info-container li i[data-selenium="hotel-star-rating"]::attr(class)').extract()
            if len(Rating) > 0:
                if 'ficon-star-1' in Rating[0]:
                    Rating = '1'
                elif 'ficon-star-2' in Rating[0]:
                    Rating = '2'
                elif 'ficon-star-3' in Rating[0]:
                    Rating = '3'
                elif 'ficon-star-4' in Rating[0]:
                    Rating = '4'
                elif 'ficon-star-5' in Rating[0]:
                    Rating = '5'
                else: Rating = ''
            else:
                Rating = ''

            Address = HotelInfo.css('ul.property-info-container li span.areacity-name span.areacity-name-text::text').extract()
            if len(Address) > 0:
                Address = Address[0].strip()
            else:
                Address = ''

            offers = []
            Info = HotelInfo.css('ul.property-info-container').xpath('li')
            if len(Info) > 2:
                Info3 =  Info[2]
                Offer = Info3.css('ol.freebies-container::attr(data-original-title)').extract()
                if len(Offer) > 0:
                    Offers = Offer[0].split('</span>')
                    for i in range(0, len(Offers)):
                        if i == len(Offers) - 1:
                            break
                        items = Offers[i].split('>')
                        item = items[len(items) - 1]
                        offers.append(item)

            OPS = []
            if len(Info) > 3:
                Info4 =  Info[3]
                Option = Info4.css('ol.freebies-container::attr(data-original-title)').extract()
                if len(Option) > 0:
                    Options = Option[0].split('</span>')
                    for i in range(0, len(Options)):
                        if i == len(Options) - 1:
                            break
                        items = Options[i].split('>')
                        item = items[len(items) - 1]
                        OPS.append(item)
            print('################ Option ####################')
            print(OPS)
            ReviewScore = PriceContainer.css('div.hotel-review-container ul.property-review-container li.review-score-container strong.review-score::text').extract()
            if len(ReviewScore) > 0:
                ReviewScore = ReviewScore[0].strip()
            else:
                ReviewScore = ''

            ReviewText = PriceContainer.css('div.hotel-review-container ul.property-review-container li.review-score-container strong.review-score-label::text').extract()
            if len(ReviewText) > 0:
                ReviewText = ReviewText[0].strip()
            else:
                ReviewText = ''

            ReviewCount = PriceContainer.css('div.hotel-review-container ul.property-review-container li.review-count-container span.review-count::text').extract()
            if len(ReviewCount) > 0:
                ReviewCount = ReviewCount[0].strip()
            else:
                ReviewCount = ''


            DetailLink = 'https://www.agoda.com/' + slugify(Name) + '/hotel/singapore-sg.html'
            
            # yield response.follow(DetailLink, callback=self.parseDetailPage, meta={
            #                                                                 'Name': Name,
            #                                                                 'Rating': Rating,
            #                                                                 'Address': Address,
            #                                                                 'YearAwarded': YearAwarded,
            #                                                                 'ReviewText': ReviewText,
            #                                                                 'ReviewScore': ReviewScore,
            #                                                                 'ReviewCount': ReviewCount,
            #                                                                 'Transports': transports,
            #                                                                 'Offers': offers,
            #                                                                 'Options': OPS,
            #                                                             })
            #         
        formdata = {
                    'PageNumber':'3',
                    'CityId': '4064',
                    'SearchType': '1',
                    'CountryId': '0'
                    }                                                   
        yield FormRequest('https://www.agoda.com/api/en-us/Main/GetSearchResultList', formdata = formdata, callback=self.myParse, method='POST')
    def myParse(self, response):
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        inspect_response(response, self)
    def parseDetailPage(self, response):
        def getItem(script, key):
            key1 = key + ': {'
            items = script.split(key1)
            if len(items) > 1:
                item = items[1].split('}')
                if len(item) > 0:
                    result = item[0]
                    return result
            return ''
        def getValue(script, key):
            key1 = key + ': '
            items = script.split(key1)
            if len(items) > 1:
                item = items[1].split('\"')
                if len(item) > 1:
                    result = item[1]
                    return result
            return ''
        
        # if response.status == 503:
        #     print('ERROR ON GETTING DATA !!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #     getch()
        # page_links = response.css('a.biz-name::attr(href)')
        # for href in page_links:
        #     yield response.follow(href, self.parseDetailPage)
        # next_page = response.css('a.next::attr(href)').extract_first()
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parseSearchPage)
        #     

        Script = response.css('script#property-page-params-init').extract()
        if len(Script) > 0:
            Script = Script[0]
        else:
            Script = ''
        Address = getItem(Script,'address')
        Address = getValue(Address1, 'full')


        Name = response.meta['Name']
        Rating = response.meta['Rating']
        YearAwarded = response.meta['YearAwarded']
        ReviewText = response.meta['ReviewText']
        ReviewScore = response.meta['ReviewScore']
        ReviewCount = response.meta['ReviewCount']
        Transports = response.meta['Transports']
        Offers = response.meta['Offers']
        Options = response.meta['Options']
        yield{
                'Name': Name,
                'Rating': Rating,
                'Address': Address,
                'YearAwarded': YearAwarded,
                'ReviewText': ReviewText,
                'ReviewScore': ReviewScore,
                'ReviewCount': ReviewCount,
                'Transports': Transports,
                'Offers': Offers,
                'Options': Options,
                'Link': response.request.url,
            }