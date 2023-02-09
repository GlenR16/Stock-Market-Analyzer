from django.core.management.base import BaseCommand,CommandError
from scrapy.crawler import CrawlerProcess
from StockMarketAnalyzer.newsScrapper.spiders.moneycontrol import NewsSpider as mc
from StockMarketAnalyzer.newsScrapper.spiders.economictimes import NewsSpider as et
import yfinance as yf

class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        
        process = CrawlerProcess()
        process.crawl(mc)
        process.crawl(et)
        process.start()
    


def getdata(stock_name):
        data = yf.Ticker(stock_name)
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
        print(df)
        #stockobj = Stock.objects.get(stock_name=stock_name)
        #today = date.today()
        #newhistory = History(stock=stockobj,open=df['Open'][i],close=df['Close'][i],date=today-timedelta(days = i+2))
        #newhistory.save()
        return None