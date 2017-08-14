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
