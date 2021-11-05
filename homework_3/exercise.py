from pprint import pprint

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from scrapper import DataClass, HHPythonScrapper


class MongoManager:
    """"""
    _instance = None  # type: MongoManager | None

    def __init__(self, db_name: str) -> None:
        self.client = MongoClient('127.0.0.1', 27017)
        self.db_name = db_name

    def __enter__(self) -> Database:
        return self.client[self.db_name]

    def __exit__(self, *args) -> None:
        self.client.close()

    @classmethod
    def get_instance(cls, db_name: str) -> 'MongoManager':
        if not cls._instance:
            cls._instance = cls(db_name)
        return cls._instance


def find_greater_salary(value: int, collection: Collection) -> list[dict]:
    return list(
        collection.find({
            "$or": [
                {"min_salary": {"$gt": value}},
                {"max_salary": {"$gt": value}}
            ]
        })
    )


if __name__ == '__main__':
    scrapper = HHPythonScrapper()
    data = scrapper.collect()  # type: list[DataClass]
    with MongoManager.get_instance('hh_data') as conn:  # type: Database
        vacancy_conn = conn.vacancy
        for vacancy in data:
            result = vacancy_conn.update_one(
                filter={"reference": {"$eq": vacancy.reference}},
                update={"$set": vacancy.__dict__},
                upsert=True
            )
        pprint(find_greater_salary(3000, vacancy_conn))
