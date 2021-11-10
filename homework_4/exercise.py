import json
from datetime import datetime

import requests
from lxml import html
from lxml.html import HtmlElement
from pymongo import MongoClient


class SourceError(Exception):
    ...


class DataContainer:
    def __init__(self, **kwargs) -> None:
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=2)


class NewsScrapper:
    """Скраппер для новостей с порталов"""
    NEWS_MAIL = "https://news.mail.ru/"
    LENTA = "https://lenta.ru/"
    NEWS_YANDEX = "https://yandex.ru/news/"
    DB_NAME = "news"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/95.0.4638.54 Safari/537.36'
    }

    def __init__(self) -> None:
        self.mongo = MongoClient('127.0.0.1', 27017)
        self.dom = None  # type: HtmlElement
        self.url = None  # type: str | None
        self.xpath = None  # type: dict | None

    def parse_source(self, source: str = None) -> None:
        match source:
            case 'mail.ru':
                self.url = self.NEWS_MAIL
                self.xpath = {
                    'list': r"//li[@class='list__item'] | "
                            r"//div[contains(@class, 'daynews__item')]",
                    'title': r".//child::text()",
                    'link': r".//a/@href"
                }
            case 'lenta.ru':
                self.url = self.LENTA
                self.xpath = r''
            case 'yandex.ru':
                self.url = self.NEWS_YANDEX
                self.xpath = r''
            case _:
                raise SourceError('Такого источника нет')
        response = requests.get(self.url, headers=self.HEADERS)
        if response.ok:
            self.dom = html.fromstring(response.text)

    def parse(self) -> list[DataContainer]:
        data_list = []  # type: list[DataContainer]
        if self.xpath:
            news_list = self.dom.xpath(self.xpath['list'])
            for news in news_list:
                data_list.append(
                    DataContainer(
                        title=news.xpath(self.xpath['title'])[0],
                        link=news.xpath(self.xpath['link'])[0],
                        pub_date=datetime.now()
                    )
                )
        return data_list

    def save_db(self, containers: list[DataContainer]) -> None:
        db = self.mongo[self.DB_NAME]
        coll = db.mail_ru
        for container in containers:
            coll.update_one(
                filter={"link": {"$eq": container.link}},
                update={"$set": container.__dict__},
                upsert=True
            )


if __name__ == '__main__':
    scrapper = NewsScrapper()
    scrapper.parse_source('mail.ru')
    data = scrapper.parse()
    scrapper.save_db(data)
    print('Done!')
