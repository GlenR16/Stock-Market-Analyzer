from django_cron import CronJobBase, Schedule
from scrapy.crawler import CrawlerProcess
from StockMarketAnalyzer.newsScrapper.spiders.moneycontrol import NewsSpider as mc
from StockMarketAnalyzer.newsScrapper.spiders.economictimes import NewsSpider as et
from StockMarketAnalyzer.newsScrapper.spiders.livemint import LivemintSpider as lm
import yfinance as yf
from home.models import Data,Stock,New,Output,Prediction
from datetime import timedelta,datetime,date
import numpy as np
from nltk.stem.porter import *
from keras_preprocessing.sequence import pad_sequences
from keras.models import load_model
from django.db.models import Avg
import pickle
import csv 
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import RobustScaler
import ta
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# stopwords_list = ["i","me","my","myself","we","our","ours","ourselves","you","you're","you've","you'll","you'd","your","yours","yourself","yourselves","he","him","his","himself","she","she's","her","hers","herself","it","it's","its","itself","they","them","their","theirs","themselves","what","which","who","whom","this","that","that'll","these","those","am","is","are","was","were","be","been","being","have","has","had","having","do","does","did","doing","a","an","the","and","but","if","or","because","as","until","while","of","at","by","for","with","about","against","between","into","through","during","before","after","above","below","to","from","up","down","in","out","on","off","over","under","again","further","then","once","here","there","when","where","why","how","all","any","both","each","few","more","most","other","some","such","no","nor","not","only","own","same","so","than","too","very","s","t","can","will","just","don","don't","should","should've","now","d","ll","m","o","re","ve","y","ain","aren","aren't","couldn","couldn't","didn","didn't","doesn","doesn't","hadn","hadn't","hasn","hasn't","haven","haven't","isn","isn't","ma","mightn","mightn't","mustn","mustn't","needn","needn't","shan","shan't","shouldn","shouldn't","wasn","wasn't","weren","weren't","won","won't","wouldn","wouldn't",]


class ScrapeNews(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'home.cron.ScrapeNews'  

    days_in_future = 5
    regfr = RandomForestRegressor()

    def do(self):
        print("Deleting old News.")
        New.objects.all().delete()
        print("Crawling News: ")
        self.crawlNews()
        print("Getting Stock Data: ")
        self.getStockData()
        print("Predicting News Sentiment: ")
        self.predictNewsSentiment()
        print("Training Supplement Models: ")
        self.trainSupplementModels()
        print("Training Main Model: ")
        self.trainMainModel()
        print("Exporting Data: ")
        self.exportCSVData()
    
    def crawlNews(self):
        process = CrawlerProcess()
        process.crawl(mc)
        process.crawl(et)
        process.crawl(lm)
        try:
            process.start()
        except Exception as e:
            return False
        else:
            return True

    def getStockData(self):
        for i in Stock.objects.all():
            if Data.objects.filter(stock=i).exists():
                self.getData(i.code,True,Data.objects.filter(stock=i).order_by("-date").first().date)
            else:
                self.getData(i.code,True)
        return True

    def predictNewsSentiment(self):
        for i in New.objects.filter(sentiment = None):
            i.sentiment = self.predictTextSentiment([i.news])
            i.save()
        return False

    def trainSupplementModels(self):
        for i in Stock.objects.all():
            if not Output.objects.filter(stock=i,date=datetime.now().date()).exists() and datetime.now().isoweekday() == 7:
                s_p = self.predictUsingSentiment(self.getCleanData(i.code),self.regfr,i.code)[0].tolist()
                h_p = self.predictUsingHistorical(i.code).tolist()
                op = Output(stock=i,sentiment_model=s_p,historical_model=h_p)
                op.save()
        return True

    def trainMainModel(self):
        for i in Stock.objects.all():
            if not Prediction.objects.filter(date__gt=datetime.now().date()).exists():
                s_op = [ i.sentiment_model for i in Output.objects.filter(stock=i).order_by("-date") ]
                h_op = [ i.historical_model for i in Output.objects.filter(stock=i).order_by("-date") ]
                a_op = [ i.get("close") for i in Data.objects.filter(stock=i).order_by('-date').values("close")[:(len(s_op)-1)*5] ]
                [ Prediction.objects.create(stock=i,date=datetime.now().date()+timedelta(index+1),close=j) for index,j in enumerate(self.finalPrediction(h_op[1:],s_op[1:],a_op,h_op[0],s_op[0])) ] 
        return True

    def exportCSVData(self):
        with open("./home/aiml/export/sentiments.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["Date", "Stock", "Sentiment"])
            for new in New.objects.all():
                writer.writerow([new.date, new.stock, new.sentiment])
        with open("./home/aiml/export/history.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["Date", "Stock", "Open", "Close"])
            for data in Data.objects.all():
                writer.writerow([data.date, data.stock, data.open, data.close])
        return True

    def getData(self,code,save = True,lastDate = datetime(2016,1,1).date()):
        data = yf.Ticker(code)
        extractDays = np.busday_count(lastDate,datetime.now().date())
        if lastDate == datetime(2016,1,1).date():
            df = data.history(period='5y')
        elif extractDays > 0:
            df = data.history(period= f"{extractDays}d",tickmode="auto")
        else:
            return None
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
    
    def predictTextSentiment(self,text):
        sentiment_analyser = load_model("./home/aiml/sentiment")
        max_len=500
        handle = open('./home/aiml/sentiment/tokenizer.pickle', 'rb')
        tokenizer = pickle.load(handle)
        xt = tokenizer.texts_to_sequences(text)
        xt = pad_sequences(xt, padding='post', maxlen=max_len)
        yt = sentiment_analyser.predict(xt).argmax(axis=1)
        sentiments = {
            0:-1,
            1:0,
            2:1
        }
        return sentiments[yt[0]]

    def getCleanData(self, stock_code):
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
        final_df = pd.DataFrame({'date':date_list,'sentiment':sentiment_vals})
        final_df['sentiment'] = final_df.sentiment.fillna(method='ffill')
        sentiment_dates = final_df['date']
        stock_dates = list(stock_df.date)
        res = list(filter(lambda i: i not in stock_dates, sentiment_dates))
        final_df.set_index('date', inplace=True)
        final_df.drop(res, axis=0, inplace=True)
        final_df['close'] = list(stock_df['close'])
        return final_df

    def predictUsingSentiment(self,final_df, model,stock_code):
        def calculate_avg(lst):
            return sum(lst) / len(lst)

        stock_values = list(final_df['close'])
        stock_values = [stock_values[i:i+self.days_in_future] for i in range(len(stock_values)-self.days_in_future)]
        sentiment_values = list(final_df['sentiment'])
        sentiment_values = [sentiment_values[i:i+self.days_in_future] for i in range(len(sentiment_values)-self.days_in_future)]
        df = pd.DataFrame({'sentiment': sentiment_values,'close_value':stock_values})
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

    def predictUsingHistorical(self,stock_code):
        historical_predictor = load_model("./home/aiml/historical")
        df= pd.DataFrame(Data.objects.filter(stock__code=stock_code).values())
        def get_technical_analysis_values(df):
            df = ta.s(df, open="open", high="high", low="low", close="close", volume="volume", fillna=True)
            df.drop(['open', 'high', 'low', 'volume'], axis=1, inplace=True)
            return df
        df = get_technical_analysis_values(df)
        df = df.drop('id', axis=1)
        df = df.drop('date', axis=1)
        df = df.drop('stock_id', axis=1)
        past_len = 1000
        n_features = df.shape[1]
        closing_val_scaler = RobustScaler()
        closing_val_scaler.fit(df[['close']])
        df_scaler = RobustScaler()
        df = pd.DataFrame(df_scaler.fit_transform(df), columns=df.columns, index=df.index)
        yhat = historical_predictor.predict(np.array(df.tail(past_len)).reshape(1, 1, past_len, n_features))
        prediction = closing_val_scaler.inverse_transform(yhat)[0]
        return prediction
    
    def finalPrediction(self,time_series_stored, sentiment_preds_stored, actual_values, time_series_prediction, sentiment_prediction):
        X=np.concatenate((np.array(time_series_stored).reshape(-1, 1), np.array(sentiment_preds_stored).reshape(-1, 1)), axis=1)
        y=actual_values
        # X = list of lists, each sub-list having 5 day predictions of each model
        # y = list of actual stock values
        svr = SVR(kernel='linear', C=1.0, epsilon=0.2)
        # trained on previously predicted values
        # print(X, y)
        assert len(X)==len(y)
        svr.fit(X, y)
        # predict on new predictions from the two models
        X_pred = np.concatenate((np.array(time_series_prediction).reshape(-1, 1), np.array(sentiment_prediction).reshape(-1, 1)), axis=1)
        y_pred = svr.predict(X_pred)
        return y_pred