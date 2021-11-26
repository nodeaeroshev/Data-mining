from typing import Iterator

import scrapy
from pymongo import MongoClient
from scrapy.exceptions import IgnoreRequest
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.media import MediaPipeline
from scrapy.spiders import Spider

from leroymerlin_parser.items import LeroymerlinParserItem

ScrapyResults = list[tuple[bool, dict[str, str]]]


class LeroymerlinParserPipeline:
    def __init__(self) -> None:
        client = MongoClient('localhost', 27017)
        self.mongodb = client['leroymerlin']

    def process_item(
            self,
            item: LeroymerlinParserItem,
            spider: Spider
    ) -> LeroymerlinParserItem:
        collect = self.mongodb[spider.name]
        collect.update_one(
            filter={'url': item['url']},
            update={'$set', item},
            upsert=True
        )
        return item


class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(
            self,
            item: LeroymerlinParserItem,
            info: MediaPipeline.SpiderInfo
    ) -> Iterator[scrapy.Request]:
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except IgnoreRequest:
                    continue

    def item_completed(
            self,
            results: ScrapyResults,
            item: LeroymerlinParserItem,
            info: MediaPipeline.SpiderInfo
    ) -> LeroymerlinParserItem:
        item['photos'] = [item[1] for item in results if item[0]]
        return item
