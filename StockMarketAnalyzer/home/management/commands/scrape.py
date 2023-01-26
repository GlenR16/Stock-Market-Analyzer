from django.core.management.base import BaseCommand,CommandError
from scrapy.crawler import CrawlerProcess
from StockMarketAnalyzer.newsScrapper.spiders.moneycontrol import NewsSpider as mc
from StockMarketAnalyzer.newsScrapper.spiders.economictimes import NewsSpider as et
class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        process = CrawlerProcess()
        process.crawl(mc)
        process.start()