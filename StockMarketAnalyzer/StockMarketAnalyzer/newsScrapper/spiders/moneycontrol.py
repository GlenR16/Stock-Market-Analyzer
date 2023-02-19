import scrapy
import re
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from StockMarketAnalyzer.newsScrapper.items import MCNewsItem
from StockMarketAnalyzer.newsScrapper.utils.utils import get_stock_id
from home.models import New,Stock
CONT_DIV = (
    '//*[@id="mc_mainWrapper"]/div[2]/div[2]/div[3]/div[2]/div[2]/div/div[3]/div[1]/div[not(@id="common_ge_widget_pricechart_news")]'
)
TITLE = "//div[2]/a/strong/text()"
LINK = "//div[2]/a/@href"
DATETIME = "//div[2]/p/text()"
DESC = '//h2[contains(@class,"article_desc")]'


def remove_ascii(text):
    if(text is None):
        return text
    text = text.encode("ascii", "ignore")
    return text.decode()

stock_ids_dict = { }
def get_urls():
    """Get urls for scraping."""
    stocks = [get_stock_id(st.code.split(".")[0]) for st in Stock.objects.all() ]
    global stock_ids_dict
    stock_ids_dict = {k:v for (k,v) in zip(stocks, [stock.code for stock in Stock.objects.all()])}
    urls = [
        f"https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id={stock_id}&durationType=M&duration=6"
        for stock_id in stocks
    ]
    return urls


def text_from_html(data):
    soup = BeautifulSoup(data, "lxml")
    for ticker in soup.find_all("a", class_=["neg", "pos"]):
        ticker.decompose()
    for script in soup.find_all("script"):
        script.decompose()
    texts = soup.findAll(text=True)
    return " ".join(t.strip('\n\t"') for t in texts)


class NewsSpider(scrapy.Spider):
    name = "moneycontrolnews"
    allowed_domains = ["www.moneycontrol.com"]
    start_urls = get_urls()

    def parse(self, response):
        rel_stock = stock_ids_dict[re.search('\?sc_id=(.*)\&durationType=', response.url).group(1)]
        news_cont = Selector(text=response.body).xpath(CONT_DIV).getall()
        for news in news_cont:
            title = Selector(text=news).xpath(TITLE).get()
            link = (
                "https://www.moneycontrol.com"
                + str(Selector(text=news).xpath(LINK).get())
            )
            if (Selector(text=news).xpath(DATETIME).get() == None):
                continue
            temp = str(Selector(text=news).xpath(
                DATETIME).get()).strip("\xa0|\xa0&nbsp;|&nbsp; Source: ")
            time, date = temp.split(" | ")
            yield scrapy.Request(
                # f"https://www.moneycontrol.com/news/services/infinte-article/?next_id={id}",
                link,
                callback=self.extract_article,
                meta={
                    "stock":rel_stock,
                    "title": title,
                    "link": link,
                    "time": time,
                    "date": date,
                    "id": id
                },
            )

    def extract_article(self, response):
        id = response.url.split("-")[-1].split(".")[0]
        desc = scrapy.Selector(text=response.body).xpath(
            f"//*[@id='article-{id}']/h2/text()").get()
        html = scrapy.Selector(text=response.body).xpath(
            f"//*[@id='article-{id}']//p/text()").getall()
        data = " ".join(html)
        data = re.split("Disclaimer", data)[0]

        news = MCNewsItem()
        news["title"] = remove_ascii(response.meta.get("title"))
        news["url"] = response.meta.get("link")
        news["id"] = id
        news["date"] = response.meta.get("date")
        news["time"] = response.meta.get("time")
        news["description"] = remove_ascii(desc)
        news["article"] = remove_ascii(data)
        if(desc != None and data != ""):
            newwws = New(headline= news["title"],news =news["article"],stock = Stock.objects.get(code=response.meta.get("stock")) )
            newwws.save()
            yield news
