import logging
import scrapy
import re
from scrapy.selector import Selector
from bs4 import BeautifulSoup
from StockMarketAnalyzer.newsScrapper.items import MCNewsItem
from StockMarketAnalyzer.newsScrapper.utils.utils import get_stock_id

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


def get_urls():
    """Get urls for scraping."""
    stocks = ["Reliance", "TCS", "HDFC Bank", "HUL", "Infosys", "ICICI Bank", "SBI", "Bharti Airtel", "Bajaj Finance", "HDFC", "ITC", "LIC India", "Adani Enterpris", "Kotak Mahindra", "Adani Total Gas", "Adani Trans", "Adani Green Ene", "Asian Paints", "Avenue Supermar", "Bajaj Finserv", "HCL Tech", "Larsen", "Maruti Suzuki", "Axis Bank", "Sun Pharma", "Titan Company", "Wipro", "Nestle", "UltraTechCement", "Adani Ports", "ONGC", "NTPC", "JSW Steel", "M&M", "Power Grid Corp", "Coal India", "Adani Power", "Pidilite Ind", "Tata Motors", "Tata Steel", "Hind Zinc", "SBI Life Insura", "HDFC Life", "Grasim", "Vedanta", "Bajaj Auto", "Ambuja Cements", "Tech Mahindra", "Siemens", "Eicher Motors", "IOC", "Dabur India",
              "Divis Labs", "IndusInd Bank", "Britannia", "Hindalco", "DLF", "Cipla", "Adani Wilmar", "Godrej Consumer", "SBI Card", "L&T Infotech", "Hindustan Aeron", "Havells India", "Shree Cements", "Bajaj Holdings", "Bharat Elec", "SRF", "ICICI Prudentia", "Dr Reddys Labs", "TATA Cons. Prod", "ABB India", "Varun Beverages", "Tata Power", "Bank of Baroda", "Interglobe Avi", "Marico", "BPCL", "Apollo Hospital", "United Spirits", "Berger Paints", "Chola Invest.", "IRCTC", "FSN E-Co Nykaa", "Page Industries", "GAIL", "ICICI Lombard", "Mindtree", "Torrent Pharma", "JSW Energy", "Zomato", "Tata Elxsi", "Schaeffler Ind", "Tube Investment", "TVS Motor", "Hero Motocorp", "INDUS TOWERS", "Patanjali Foods", "UPL", "Trent"]
    # stocks = ["Reliance", "TCS", "HDFC Bank", "HUL"]
    stock_ids = [get_stock_id(stock) for stock in stocks]
    print(stock_ids)
    urls = [
        f"https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id={stock_id}&durationType=M&duration=1"
        for stock_id in stock_ids
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
            yield news
