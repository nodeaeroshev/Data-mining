import scrapy


class InstaparserItem(scrapy.Item):
    _id = scrapy.Field()
    username = scrapy.Field()
    collect_name = scrapy.Field()
    users = scrapy.Field()
