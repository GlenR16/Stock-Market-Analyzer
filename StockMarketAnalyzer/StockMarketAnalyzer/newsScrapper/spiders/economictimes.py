from bs4 import BeautifulSoup
import scrapy
from scrapy.selector import Selector
from StockMarketAnalyzer.newsScrapper.items import NewsItem


# Constant XPaths
#    Story XPaths
STORY = "/html/body/div/div"
STORY_TITLE = "//h3/a/text()"
STORY_LINK = "//h3/a/@href"
STORY_TYPE = "//span/text()"
STORY_DATE = "//div[1]/time/text()"
STORY_SUMMARY = "//p/text()"
#    Article XPaths
ARTICLEDIV = "//div/div[1]/div[3]/div/article/div[contains(@class, 'artText')]"
NSE_INDICATORS = "//a[contains(@class, 'neg') or contains(@class, 'pos')]"


def get_urls():
    # res = requests.get("").json()
    res = list(range(10))
    urls = [
        f"https://economictimes.indiatimes.com/stocksupdate_news/companyid-{stock_id}.cms"
        for stock_id in res
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
    name = "economictimes"
    allowed_domains = ["economictimes.indiatimes.com"]
    start_urls = get_urls()

    def parse(self, response):
        stories = Selector(text=response.body).xpath(STORY).getall()
        if stories == None or stories == "":
            yield {"Not connected"}
        for story in stories:
            title = Selector(text=story).xpath(STORY_TITLE).get()
            link = "https://economictimes.indiatimes.com" + \
                str(Selector(text=story).xpath(STORY_LINK).get())

            type = str(Selector(text=story).xpath(STORY_TYPE).get()).split("| ")[1]
            date=Selector(text=story).xpath(STORY_DATE).get()
            summary=Selector(text=story).xpath(STORY_SUMMARY).get()
            yield scrapy.Request(
                link,
                callback=self.extract_article,
                meta={
                    "title": title,
                    "link": link,
                    "type": type,
                    "date": date,
                    "summary": summary,
                },
            )

    def extract_article(self, response):
        html=scrapy.Selector(text=response.body).xpath(ARTICLEDIV).get()
        if html is None:
            return
        data=text_from_html(html)
        news=NewsItem()
        news["title"]=response.meta.get("title")
        news["url"]=response.meta.get("link")
        news["type"]=response.meta.get("type")
        news["date"]=response.meta.get("date")
        news["summary"]=response.meta.get("summary")
        news["article"]=data
        yield news
