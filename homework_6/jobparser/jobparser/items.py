import scrapy


class JobparserItem(scrapy.Item):
    name = scrapy.Field()
    salary = scrapy.Field()
    url = scrapy.Field()


class MongoItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    salary_from = scrapy.Field()
    salary_to = scrapy.Field()
    url = scrapy.Field()
