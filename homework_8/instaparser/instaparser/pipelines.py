from pymongo import MongoClient
from scrapy.item import Item
from scrapy.spiders import Spider


class InstaparserPipeline:
    def __init__(self) -> None:
        client = MongoClient('localhost', 27017)
        self.mongodb = client['web']

    def process_item(self, item: Item, spider: Spider) -> Item:
        collect = self.mongodb[spider.name]
        collect.update_one(
            filter={'_id': item['_id']},
            update={'$set', item},
            upsert=True
        )
        return item
