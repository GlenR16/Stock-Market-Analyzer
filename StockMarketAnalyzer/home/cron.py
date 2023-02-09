from django_cron import CronJobBase, Schedule
from scrapy.crawler import CrawlerProcess
from StockMarketAnalyzer.newsScrapper.spiders.moneycontrol import NewsSpider as mc
from StockMarketAnalyzer.newsScrapper.spiders.economictimes import NewsSpider as et
import yfinance as yf
from home.models import Data,Stock,New
from datetime import date
from datetime import timedelta

class ScrapeNews(CronJobBase):
    RUN_EVERY_MINS = 1 
    RETRY_AFTER_FAILURE_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'home.cron.ScrapeNews'  

    def do(self):
        print("Deleting old data -->")
        New.objects.all().delete()
        Data.objects.all().delete()
        print("Getting News -->")
        process = CrawlerProcess()
        process.crawl(mc)
        process.crawl(et)
        process.start()
        print("Getting Stock Data -->")
        for i in Stock.objects.all():
            self.getdata(i.code)
        #model called
        #gets sentiment average
        #nerual network predict
        #SAve to history db



    def getdata(self,code):
        data = yf.Ticker(code)
        df = data.history(period='1mo')
        cols = list(df.columns)
        if 'Dividends' in cols:
            df = df.drop('Dividends', axis=1)
        if 'Stock Splits' in cols:
            df = df.drop('Stock Splits', axis=1)
        if 'High' in cols:
            df = df.drop('High', axis=1)
        if 'Low' in cols:
            df = df.drop('Low', axis=1)
        if 'Volume' in cols:
            df = df.drop('Volume', axis=1)
        df.reset_index(drop=True, inplace=True)
        stockobj = Stock.objects.get(code=code)
        today = date.today()
        for i in df.index:
            #Handle saturdays sundays
            newdata = Data(stock=stockobj,open=df['Open'][i],close=df['Close'][i],date=today-timedelta(days = 21-i+1))
            newdata.save()
        return None