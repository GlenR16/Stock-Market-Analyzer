import scrapy
from StockMarketAnalyzer.newsScrapper.items import LiveMintNewsItem
from home.models import New, Stock
from datetime import datetime
import urllib.parse
import re

headers = {
    "Host": "www.livemint.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cookie": "lm-location=IN",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Connection": "keep-alive",
    "TE": "trailers",
}

stock_ids_dict = {}


def get_urls():
    """Get urls for scraping."""
    stocks = [urllib.parse.quote(st.name) for st in Stock.objects.all()]
    global stock_ids_dict
    stock_ids_dict = {
        k: v for (k, v) in zip(stocks, [stock.code for stock in Stock.objects.all()])
    }
    urls = [
        f"https://www.livemint.com/searchlisting/1/{stock_query}"
        for stock_query in stocks
    ]
    return urls


class LivemintSpider(scrapy.Spider):
    name = "livemint"
    allowed_domains = ["livemint.com"]
    start_urls = get_urls()
    handle_httpstatus_list = [403]
    # start_urls = ["https://www.livemint.com/searchlisting/1/Reliance%20Industries"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response):
        reached_end = False
        rel_stock = stock_ids_dict[response.url.split("/")[-1]]
        for article in response.css(".listingNew"):
            heading = article.css("div > .headlineSec > h2 > a::text").extract_first()
            link = article.css(
                "div > .headlineSec > h2 > a::attr(href)"
            ).extract_first()
            link = urllib.parse.urljoin(response.url, link)
            date_time = article.css(
                "div > .headlineSec > span> span::attr(data-updatedtime)"
            ).extract_first()
            datetime_obj = datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
            if (datetime.now() - datetime_obj).days > 180:
                reached_end = True
            yield scrapy.Request(
                link,
                headers=headers,
                callback=self.parse_article,
                meta={"heading": heading, "datetime": date_time, "stock": rel_stock},
            )
        if not reached_end:
            current_url = response.url
            next_page = "/".join(
                current_url.rsplit("/")[:-2]
                + [str(int(current_url.rsplit("/")[-2]) + 1)]
                + current_url.rsplit("/")[-1:]
            )
            yield scrapy.Request(next_page, headers=headers, callback=self.parse)

    def parse_article(self, response):
        date_time = datetime.strptime(
            response.meta.get("datetime"), "%Y-%m-%dT%H:%M:%S"
        )
        news_id = re.search(r"(\d+)\.html$", response.url)
        item = LiveMintNewsItem()
        item["title"] = response.meta.get("heading")
        item["date"] = date_time.date()
        item["time"] = date_time.time()
        item["article"] = response.css("#mainArea p::text").getall()
        item["url"] = response.url
        item["id"] = news_id.group(1) if news_id else None
        item["description"] = response.css(
            "meta[name=description]::attr(content)"
        ).get()
        if item["article"] != None:
            newwws = New(
                headline=item["title"],
                news=item["article"],
                date=date_time.strftime("%Y-%m-%d"),
                stock=Stock.objects.get(code=response.meta.get("stock")),
            )
            newwws.save()
            yield item
