# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AgodaReviewItem(scrapy.Item):
    # define the fields for your item here like:
	title 				= scrapy.Field()
	comment 			= scrapy.Field()
	language			= scrapy.Field()
	date_publish		= scrapy.Field()
	date_publish_timestamp		= scrapy.Field()
	product_id			= scrapy.Field()
	review_score		= scrapy.Field()
	rating_out_of		= scrapy.Field()
	author				= scrapy.Field()
	country				= scrapy.Field()
	type_of_trip		= scrapy.Field()
	room_type			= scrapy.Field()
	details_stay		= scrapy.Field()
	link				= scrapy.Field()
	# data_provider_id	= scrapy.Field()
	product_name		= scrapy.Field()
	source_sentiment	= scrapy.Field()

class CtripItem(scrapy.Item):
    # define the fields for your item here like:
	# title 				= scrapy.Field()
	comment 				= scrapy.Field()
	detected_lang		= scrapy.Field()
	detected_lang_text	= scrapy.Field()
	published_date_1	= scrapy.Field()
	published_date		= scrapy.Field()
	product_id			= scrapy.Field()
	rating				= scrapy.Field()
	rating_outof		= scrapy.Field()
	author				= scrapy.Field()
	# country				= scrapy.Field()
	# reviewer_group		= scrapy.Field()
	# room_type			= scrapy.Field()
	# stay_detail			= scrapy.Field()
	url					= scrapy.Field()
	# data_provider_id	= scrapy.Field()
	product_name		= scrapy.Field()