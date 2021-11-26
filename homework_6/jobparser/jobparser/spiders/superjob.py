from typing import Callable, Iterator

import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import JobparserItem

ScrapyParse = Iterator[Callable[[HtmlResponse], None]]


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response: HtmlResponse) -> ScrapyParse:
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath(
            "//span[@class='_1e6dO _1XzYb _2EZcW']/a/@href"
        ).getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse) -> ScrapyParse:
        name = response.xpath("//h1/text()").get()
        salary = response.xpath(
            "//span[@class='_1OuF_ ZON4b']/span/text()"
        ).getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
