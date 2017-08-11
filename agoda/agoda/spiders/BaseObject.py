import ConfigParser, os

class baseConfig:
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('agoda/spiders/config.cfg')
        self.branch_name = self.config['branch_name']
        # self.constant = self.config['constant']['constant1']

class bookingConfig(baseConfig):
    def __init__(self):
        super().__init__()
        self.css_sites_PSP = self.config['booking.com']['css_sites_parseSearchPage']
        self.css_hotelname_PSP = self.config['booking.com']['css_hotel_name_parseSearchPage']
        self.css_href_PSP = self.config['booking.com']['css_href_parsesearchpage']
        self.css_next_page_PSP = self.config['booking.com']['css_next_page_parsesearchpage']
        self.css_href_PDP = self.config['booking.com']['css_href_parseDetailPage']
        self.css_reviews_PRs = self.config['booking.com']['css_reviews_parseReviews']
        self.css_check_PreviousPage_PRs = self.config['booking.com']['css_check_PreviousPage_parseReviews']
        self.css_datePublish_PRs = self.config['booking.com']['css_datePublish_parseReviews']
        self.css_author_PRs = self.config['booking.com']['css_author_parseReviews']
        self.css_review_score_PRs = self.config['booking.com']['css_review_score_parseReviews']
        self.css_country_PRs = self.config['booking.com']['css_country_parseReviews']
        self.css_negative_PRs = self.config['booking.com']['css_negative_parseReviews']
        self.css_positive_PRs = self.config['booking.com']['css_positive_parseReviews']
        self.css_tags_PRs = self.config['booking.com']['css_tags_parseReviews']
        self.css_title_PRs = self.config['booking.com']['css_title_parseReviews']
        self.css_next_page_PRs = self.config['booking.com']['css_next_page_parseReviews']
        self.path = self.config['url']['booking']
        self.filter_language = self.config['booking_filter_language']
        self.type_of_trip = self.config['booking_type_of_trip']



class tripadvisorConfig(baseConfig):
    def __init__(self):
        super().__init__()
        self.css_total_page_PSP = self.config['tripadvisor.com']['css_total_page_PSP']
        self.css_sites_PLP = self.config['tripadvisor.com']['css_sites_PLP']
        self.css_hotel_name_PLP = self.config['tripadvisor.com']['css_hotel_name_PLP']
        self.css_href_PLP = self.config['tripadvisor.com']['css_href_PLP']
        self.css_total_page_PFL = self.config['tripadvisor.com']['css_total_page_PFL']
        self.css_reviews_QR = self.config['tripadvisor.com']['css_reviews_QR']
        self.css_reviews_PRs = self.config['tripadvisor.com']['css_reviews_PRs']
        self.css_stayed_PRs = self.config['tripadvisor.com']['css_stayed_PRs']
        self.css_author_PRs = self.config['tripadvisor.com']['css_author_PRs']
        self.css_country_PRs = self.config['tripadvisor.com']['css_country_PRs']
        self.css_datePublish_PRs = self.config['tripadvisor.com']['css_datePublish_PRs']
        self.css_title_PRs = self.config['tripadvisor.com']['css_title_PRs']
        self.css_entries_PRs = self.config['tripadvisor.com']['css_entries_PRs']
        self.css_entry_PRs = self.config['tripadvisor.com']['css_entry_PRs']
        self.path = self.config['url']['tripadvisor']
        self.filter_language = self.config['tripadvisor_filter_language']
        self.header = self.config['header']['header_booking']
