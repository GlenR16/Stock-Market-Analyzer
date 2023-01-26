import scrapy


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    type = scrapy.Field()
    date = scrapy.Field()
    summary = scrapy.Field()
    article = scrapy.Field()


class MCNewsItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    date = scrapy.Field()
    time = scrapy.Field()
    description = scrapy.Field()
    article = scrapy.Field()
