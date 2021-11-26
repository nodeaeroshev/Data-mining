import scrapy
from itemloaders.processors import MapCompose, TakeFirst


class LeroymerlinParserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(
        input_processor=MapCompose(
            lambda x: int(x.replace(' ', ''))
        ),
        output_processor=TakeFirst()
    )
    value = scrapy.Field(output_processor=TakeFirst())
