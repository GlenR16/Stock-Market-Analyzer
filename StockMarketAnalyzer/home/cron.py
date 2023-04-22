from django_cron import CronJobBase, Schedule
from scrapy.crawler import CrawlerProcess
from StockMarketAnalyzer.newsScrapper.spiders.moneycontrol import NewsSpider as mc
from StockMarketAnalyzer.newsScrapper.spiders.economictimes import NewsSpider as et
from StockMarketAnalyzer.newsScrapper.spiders.livemint import LivemintSpider as lm
import yfinance as yf
from home.models import Data,Stock,New
from datetime import timedelta,datetime,date
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
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import RobustScaler
import ta


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
    sentiment_analyser = load_model("./home/aiml/sentiment")
    historical_predictor = load_model("./home/aiml/historical")
    RUN_EVERY_MINS = 1 
    RETRY_AFTER_FAILURE_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'home.cron.ScrapeNews'  

    days_in_future = 5
    regfr = RandomForestRegressor()

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
            s_p = self.predict_using_sentiment(self.get_clean_data(i.code),self.regfr,i.code)
            h_p = self.predict_using_historical(i.code)
            print(i.name , "->",s_p,h_p)


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
        


    def getdata(self,code,save = True):
        data = yf.Ticker(code)
        df = data.history(period='5y')
        cols = list(df.columns)
        if 'Dividends' in cols:
            df = df.drop('Dividends', axis=1)
        if 'Stock Splits' in cols:
            df = df.drop('Stock Splits', axis=1)
        stockobj = Stock.objects.get(code=code)
        if save:
            for i in df.index:
                newdata = Data(stock=stockobj,open=df['Open'][i],close=df['Close'][i],high=df['High'][i],low=df['Low'][i],volume=df['Volume'][i],date=i+timedelta(days = 1))
                newdata.save()
        return df
    
    def predict_sentiment(self,text):
        max_len=500
        handle = open('./home/aiml/sentiment/tokenizer.pickle', 'rb')
        tokenizer = pickle.load(handle)
        xt = tokenizer.texts_to_sequences(text)
        xt = pad_sequences(xt, padding='post', maxlen=max_len)
        yt = self.sentiment_analyser.predict(xt).argmax(axis=1)
        sentiments = {
            0:-1,
            1:0,
            2:1
        }
        return sentiments[yt[0]]

    def get_clean_data(self, stock_code):
        sentiment_df = pd.DataFrame(list(New.objects.filter(stock__code=stock_code).order_by("date").values("date","sentiment","stock")))
        stock_df = pd.DataFrame(Data.objects.filter(stock__code=stock_code,date__gte=New.objects.filter(stock__code=stock_code).order_by("date").first().date).values("date","stock","close"))
        idx = list(range(len(stock_df)))
        stock_df['idx'] = idx
        sentiment_df.drop('stock', axis=1, inplace=True)
        sentiment_df.set_index('date', inplace=True)
        date_list = list(pd.date_range(start=sentiment_df.index.min(), end=date.today()))
        date_list = [ i.to_pydatetime().date() for i in  date_list ]
        sentiment_df = sentiment_df.groupby('date').mean()
        sentiment_vals=[]
        threshold=14
        count=0
        for i in date_list:
            try:
                sentiment_vals.append(sentiment_df.loc[i].sentiment)
            except KeyError:
                if count==threshold:
                    count=0
                    sentiment_vals.append(0)
                else:
                    sentiment_vals.append(None)
                count+=1
        final_df = pd.DataFrame({
        'date':date_list,
        'sentiment':sentiment_vals
        })
        final_df['sentiment'] = final_df.sentiment.fillna(method='ffill')
        sentiment_dates = final_df['date']
        stock_dates = list(stock_df.date)
        res = list(filter(lambda i: i not in stock_dates, sentiment_dates))
        final_df.set_index('date', inplace=True)
        final_df.drop(res, axis=0, inplace=True)
        final_df['close'] = list(stock_df['close'])
        return final_df

    def predict_using_sentiment(self,final_df, model,stock_code):

        def calculate_avg(lst):
            return sum(lst) / len(lst)
        stock_values = list(final_df['close'])

        stock_values = [stock_values[i:i+self.days_in_future] for i in range(len(stock_values)-self.days_in_future)]
        sentiment_values = list(final_df['sentiment'])
        sentiment_values = [sentiment_values[i:i+self.days_in_future] for i in range(len(sentiment_values)-self.days_in_future)]
        df = pd.DataFrame({
        'sentiment': sentiment_values,
        'close_value':stock_values
        })
        df['sentimentavg'] = df['sentiment'].apply(calculate_avg)
        x=list(df['sentimentavg'])
        y=list(df['close_value'])
        x = [[i] for i in x]
        regfr = model
        regfr.fit(x, y)
        todays_sentiment=New.objects.filter(stock__code=stock_code).order_by("date").first().sentiment
        predict = list(df['sentiment'].tail(1))[0]
        predict = predict[-4:]
        predict.append(todays_sentiment)
        return regfr.predict([[np.average(predict)]])


    def predict_using_historical(self,stock_code):
        df = self.getdata(stock_code,False)
        # df= pd.DataFrame(Data.objects.filter(stock__code=stock_code).values())

        def get_technical_analysis_values(df):
            df = ta.add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True)
            df.drop(['Open', 'High', 'Low', 'Volume'], axis=1, inplace=True)
            return df
        df = get_technical_analysis_values(df)
        # df = df.drop('id', axis=1)
        # df = df.drop('date', axis=1)
        # df = df.drop('stock_id', axis=1)
        past_len = 1000
        n_features = df.shape[1]
        closing_val_scaler = RobustScaler()
        closing_val_scaler.fit(df[['Close']])
        df_scaler = RobustScaler()
        df = pd.DataFrame(df_scaler.fit_transform(df), columns=df.columns, index=df.index)
        yhat = self.historical_predictor.predict(np.array(df.tail(past_len)).reshape(1, 1, past_len, n_features))
        prediction = closing_val_scaler.inverse_transform(yhat)[0]
        return prediction