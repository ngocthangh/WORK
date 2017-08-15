import configparser, os
import json
from agoda.spiders.BaseObject import baseConfig

SOURCE_AGODA = 'agoda.com'

class ConfigurationManager(baseConfig):
	def __init__(self):
		super().__init__()
		# self.config = configparser.ConfigParser()
		# self.config.read('agoda/spiders/config.cfg')
		self.RATING_OUT_OF = self.config.get(SOURCE_AGODA, 'RATING_OUT_OF')
		self.INSERTDB = self.config.getboolean(SOURCE_AGODA, 'INSERTDB')
		self.BRANCH = json.loads(self.config.get(SOURCE_AGODA, 'BRANCH'))
		self.LANGUAGE = self.config.get(SOURCE_AGODA, 'LANGUAGE')
		self.REVIEW_PER_PAGE = self.config.get(SOURCE_AGODA, 'REVIEW_PER_PAGE')
		self.HEADER = self.config.get(SOURCE_AGODA, 'HEADER')
		self.HEADER_REVIEW = self.config.get(SOURCE_AGODA, 'HEADER_REVIEW')
		self.DB_NAME = self.config[SOURCE_AGODA]['DB_NAME']

		self.css_body_1 = self.config[SOURCE_AGODA]['css_body_1'] 
		self.css_reviews_1_1 = self.config[SOURCE_AGODA]['css_reviews_1_1'] 

		self.css_review_id_1_1_1 = self.config[SOURCE_AGODA]['css_review_id_1_1_1'] 
		self.css_review_info_1_1_2 = self.config[SOURCE_AGODA]['css_review_info_1_1_2'] 
		self.css_review_detail_1_1_3 = self.config[SOURCE_AGODA]['css_review_detail_1_1_3'] 

		self.css_review_score_1_1_2_1 = self.config[SOURCE_AGODA]['css_review_score_1_1_2_1'] 
		self.css_reviewer_name_1_1_2_2 = self.config[SOURCE_AGODA]['css_reviewer_name_1_1_2_2'] 
		self.css_reviewer_nation_1_1_2_3 = self.config[SOURCE_AGODA]['css_reviewer_nation_1_1_2_3'] 
		self.css_traveler_type_1_1_2_4 = self.config[SOURCE_AGODA]['css_traveler_type_1_1_2_4'] 
		self.css_room_type_1_1_2_5 = self.config[SOURCE_AGODA]['css_room_type_1_1_2_5'] 
		self.css_detail_stayed_1_1_2_6 = self.config[SOURCE_AGODA]['css_detail_stayed_1_1_2_6'] 

		self.css_review_date_1_1_3_1 = self.config[SOURCE_AGODA]['css_review_date_1_1_3_1'] 
		self.css_review_date_1_1_3_2 = self.config[SOURCE_AGODA]['css_review_date_1_1_3_2'] 
		self.css_review_title_1_1_3_3 = self.config[SOURCE_AGODA]['css_review_title_1_1_3_3'] 
		self.css_positive_review_1_1_3_4 = self.config[SOURCE_AGODA]['css_positive_review_1_1_3_4'] 
		self.css_negative_review_1_1_3_5 = self.config[SOURCE_AGODA]['css_negative_review_1_1_3_5'] 
		self.css_review_text_1_1_3_6 = self.config[SOURCE_AGODA]['css_review_text_1_1_3_6'] 


	def test(self):
		config = ConfigParser.RawConfigParser()

		# When adding sections or items, add them in the reverse order of
		# how you want them to be displayed in the actual file.
		# In addition, please note that using RawConfigParser's and the raw
		# mode of ConfigParser's respective set functions, you can assign
		# non-string values to keys internally, but will receive an error
		# when attempting to write to a file or when you get it in non-raw
		# mode. SafeConfigParser does not allow such assignments to take place.
		config.add_section('Section1')
		config.set('Section1', 'an_int', '15')
		config.set('Section1', 'a_bool', 'true')
		config.set('Section1', 'a_float', '3.1415')
		config.set('Section1', 'baz', 'fun')
		config.set('Section1', 'bar', 'Python')
		config.set('Section1', 'foo', '%(bar)s is %(baz)s!')

		# Writing our configuration file to 'example.cfg'
		with open('config.cfg', 'wb') as configfile:
		    config.write(configfile)
		print('write successfully!')