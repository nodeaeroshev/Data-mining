from typing import Callable, Iterator

import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import JobparserItem

ScrapyParse = Iterator[Callable[[HtmlResponse], None]]


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://hh.ru/search/vacancy?&fromSearchLine=true&text=python'
    ]

    def parse(self, response: HtmlResponse) -> ScrapyParse:
        next_page = response.xpath(
            "//a[@data-qa='pager-next']/@href"
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath(
            "//a[@data-qa='vacancy-serp__vacancy-title']/@href"
        ).getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse) -> ScrapyParse:
        name = response.xpath("//h1/text()").get()
        salary = response.xpath(
            "//div[@class='vacancy-salary']/span/text()"
        ).getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
