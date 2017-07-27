# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AgodaReviewItem(scrapy.Item):
    # define the fields for your item here like:
	title 				= scrapy.Field()
	text 				= scrapy.Field()
	detect_lang			= scrapy.Field()
	published_date_1	= scrapy.Field()
	published_date		= scrapy.Field()
	product_id			= scrapy.Field()
	rating				= scrapy.Field()
	rating_outof		= scrapy.Field()
	author				= scrapy.Field()
	country				= scrapy.Field()
	reviewer_group		= scrapy.Field()
	room_type			= scrapy.Field()
	stay_detail			= scrapy.Field()
	url					= scrapy.Field()
	data_provider_id	= scrapy.Field()
	product_name		= scrapy.Field()
