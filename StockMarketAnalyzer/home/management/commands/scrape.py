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
    
def get_stock_data(stock_name):
    data = yf.Ticker(stock_name)
    df = data.history(period='1mo')
    cols = list(df.columns)
    if 'Dividends' in cols:
        df = df.drop('Dividends', axis=1)
    if 'Stock Splits' in cols:
        df = df.drop('Stock Splits', axis=1)
    df.reset_index(drop=True, inplace=True)
    return df    

