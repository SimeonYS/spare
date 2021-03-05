import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import SpareItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class SpareSpider(scrapy.Spider):
	name = 'spare'
	start_urls = ['https://www.spardjurs.dk/Nyheder?doshow27=1']

	def parse(self, response):
		articles = response.xpath('//div[@class="modulelayout27_2"]')
		for article in articles:
			date = article.xpath('.//div[@class="vdcontent"]//text()').getall()[0]
			post_links = article.xpath('.//a[@class="layoutbox module27_2_layoutbox1"]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="PagePosition NavigateNext"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,date):
		title = response.xpath('//h1[@class="heading-h1"]/text()').get()
		content = response.xpath('//div[@id="layout27sub1mergefield5"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SpareItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
