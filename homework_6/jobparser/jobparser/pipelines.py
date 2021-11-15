from typing import MutableMapping

from pymongo import MongoClient
from scrapy import Spider

from jobparser.items import MongoItem


class JobparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client['vacancies']

    def process_item(
        self,
        item: MutableMapping,
        spider: Spider
    ) -> MutableMapping:
        mongo_item = self.process_salary(item)
        collection = self.mongo_base[spider.name]
        collection.insert_one(mongo_item)
        return item

    @staticmethod
    def process_salary(item: MutableMapping) -> MongoItem:
        salary = []  # type: list[int]
        for cell in item.get('salary', []):
            try:
                salary.append(int(''.join(cell.split())))
            except ValueError:
                continue
        iter_salary = iter(salary)
        return MongoItem(
            name=item.get('name', None),
            salary_from=next(iter_salary, None),
            salary_to=next(iter_salary, None),
            url=item.get('url', None)
        )
