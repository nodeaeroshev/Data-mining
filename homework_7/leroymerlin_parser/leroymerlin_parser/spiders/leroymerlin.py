from typing import Callable, Iterator

import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from leroymerlin_parser.items import LeroymerlinParserItem

ScrapyParse = Iterator[Callable[[HtmlResponse], None]]


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru/search/?q={query}']

    def __init__(self, *args, **kwargs) -> None:
        super(LeroymerlinSpider, self).__init__(*args, **kwargs)
        self.start_urls = [
            url.format(query=kwargs.get('query', ''))
            for url in self.start_urls
        ]

    def parse(self, response: HtmlResponse, **kwargs) -> ScrapyParse:
        next_page = response.xpath(
            "//div[@role='navigation']/div/a[2]/@href"
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath(
            "//section[@class='p7w1ji8_plp']/div/div/a/@href"
        ).getall()
        for link in links:
            yield response.follow(link, callback=self.parse_good)

    def parse_good(self, response: HtmlResponse) -> ScrapyParse:
        loader = ItemLoader(item=LeroymerlinParserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath(
            'photos',
            "//picture[@slot='pictures']/source[1]/@srcset"
        )
        loader.add_value('url', response.url)
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('value', "//span[@slot='currency']/text()")
        yield loader.load_item()
