from django_cron import CronJobBase, Schedule
from scrapy.crawler import CrawlerProcess
from StockMarketAnalyzer.newsScrapper.spiders.moneycontrol import NewsSpider as mc
from StockMarketAnalyzer.newsScrapper.spiders.economictimes import NewsSpider as et
from StockMarketAnalyzer.newsScrapper.spiders.livemint import LivemintSpider as lm
import yfinance as yf
from home.models import Data, Stock, New
from datetime import timedelta, datetime
import numpy as np
import re
from nltk.stem.porter import *
from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from keras.models import load_model
from django.db.models import Avg
import pickle
import csv

stopwords_list = [
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "you're",
    "you've",
    "you'll",
    "you'd",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "she's",
    "her",
    "hers",
    "herself",
    "it",
    "it's",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "that'll",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "don't",
    "should",
    "should've",
    "now",
    "d",
    "ll",
    "m",
    "o",
    "re",
    "ve",
    "y",
    "ain",
    "aren",
    "aren't",
    "couldn",
    "couldn't",
    "didn",
    "didn't",
    "doesn",
    "doesn't",
    "hadn",
    "hadn't",
    "hasn",
    "hasn't",
    "haven",
    "haven't",
    "isn",
    "isn't",
    "ma",
    "mightn",
    "mightn't",
    "mustn",
    "mustn't",
    "needn",
    "needn't",
    "shan",
    "shan't",
    "shouldn",
    "shouldn't",
    "wasn",
    "wasn't",
    "weren",
    "weren't",
    "won",
    "won't",
    "wouldn",
    "wouldn't",
]


class ScrapeNews(CronJobBase):
    model = load_model("./home/aiml/sentiment")
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1
    schedule = Schedule(
        run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS
    )
    code = "home.cron.ScrapeNews"

    def do(self):
        print("Deleting old News and Data.")
        New.objects.all().delete()
        Data.objects.all().delete()
        print("Getting News (6 Months).")
        process = CrawlerProcess()
        process.crawl(mc)
        process.crawl(et)
        process.crawl(lm)
        process.start()
        print("Getting Stock Data (6 Months).")
        for i in Stock.objects.all():
            self.getdata(i.code)
        print("Predicting sentiment.")
        for i in New.objects.all():
            i.sentiment = self.predict_sentiment([i.news])
            i.save()
        print("Training Model.")
        for i in Stock.objects.all():
            pass
        print("Predicting stock prices.")
        for i in Stock.objects.all():
            inputData = 0
            if (
                New.objects.filter(
                    stock=i, date__gte=datetime.now().date() - timedelta(days=14)
                ).count()
                != 0
            ):
                inputData = New.objects.filter(
                    stock=i,
                    date=New.objects.filter(
                        stock=i, date__gte=datetime.now().date() - timedelta(days=14)
                    )
                    .order_by("-date")
                    .first()
                    .date,
                ).aggregate(Avg("sentiment"))
            print("Final for", i, " : ", inputData)
        print("Exporting Data.")
        with open("./home/aiml/export/sentiments.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["Date", "Stock", "Sentiment"])
            for new in New.objects.all():
                writer.writerow([new.date, new.stock, new.sentiment])
        print("Export to ./home/aiml/export/sentiments.csv")
        with open("./home/aiml/export/history.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["Date", "Stock", "Open", "Close"])
            for data in Data.objects.all():
                writer.writerow([data.date, data.stock, data.open, data.close])
        print("Export to ./home/aiml/export/history.csv")

    def getdata(self, code):
        data = yf.Ticker(code)
        df = data.history(period="6mo")
        cols = list(df.columns)
        if "Dividends" in cols:
            df = df.drop("Dividends", axis=1)
        if "Stock Splits" in cols:
            df = df.drop("Stock Splits", axis=1)
        if "High" in cols:
            df = df.drop("High", axis=1)
        if "Low" in cols:
            df = df.drop("Low", axis=1)
        if "Volume" in cols:
            df = df.drop("Volume", axis=1)
        stockobj = Stock.objects.get(code=code)
        for i in df.index:
            newdata = Data(
                stock=stockobj,
                open=df["Open"][i],
                close=df["Close"][i],
                date=i + timedelta(days=1),
            )
            newdata.save()
        return None

    def predict_sentiment(self, text):
        max_len = 500
        handle = open("./home/aiml/sentiment/tokenizer.pickle", "rb")
        tokenizer = pickle.load(handle)
        xt = tokenizer.texts_to_sequences(text)
        xt = pad_sequences(xt, padding="post", maxlen=max_len)
        yt = self.model.predict(xt).argmax(axis=1)
        sentiments = {0: -1, 1: 0, 2: 1}
        return sentiments[yt[0]]
