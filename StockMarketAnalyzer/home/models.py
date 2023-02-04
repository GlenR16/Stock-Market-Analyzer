from django.db import models
import datetime

class Stock(models.Model):
    stock_id = models.AutoField(primary_key = True,editable = False)
    stock_name = models.CharField(max_length=63)
    close = models.FloatField()
    predicted_close = models.FloatField()
    def __str__(self) -> str:
        return f"{self.stock_name}"

class User(models.Model):
    user_id = models.AutoField(primary_key = True,editable = False)
    name = models.CharField(max_length=63)
    email = models.EmailField(unique=True,max_length=127)
    password = models.CharField(max_length=63)
    dateCreated = models.DateField(default=datetime.datetime.utcnow,editable=False)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL,blank=True,null=True)

class New(models.Model):
    news_id = models.AutoField(primary_key = True,editable = False)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE,blank=True,null=True)
    headline = models.CharField(max_length=255,blank=True)
    news = models.TextField()
    sentiment = models.FloatField(blank=True,null=True)
    def __str__(self) -> str:
        return f"{self.headline}"
    
class History(models.Model):
    date = models.DateField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    open = models.FloatField(default=0)
    close = models.FloatField(default=0)
