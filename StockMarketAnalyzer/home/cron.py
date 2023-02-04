from django_cron import CronJobBase, Schedule
from scrapy.crawler import CrawlerProcess
from StockMarketAnalyzer.newsScrapper.spiders.moneycontrol import NewsSpider as mc
from StockMarketAnalyzer.newsScrapper.spiders.economictimes import NewsSpider as et

class ScrapeNews(CronJobBase):
    RUN_EVERY_MINS = 1 
    RETRY_AFTER_FAILURE_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'home.cron.ScrapeNews'  

    def do(self):
        print("Running Scraper -->")
        process = CrawlerProcess()
        process.crawl(mc)
        process.crawl(et)
        process.start()