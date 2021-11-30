from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instaparser import settings
from instaparser.spiders import InstaSpider

if __name__ == '__main__':
    load_dotenv()
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstaSpider, users=['tapaevadaniya', 'onliskill_udm'])
    process.start()
