from django.db import models
import datetime

class Stock(models.Model):
    sid = models.AutoField(primary_key = True,editable = False)
    name = models.CharField(max_length=63)
    code = models.CharField(unique=True,max_length=10)
    def __str__(self) -> str:
        return f"{self.name}"

class User(models.Model):
    uid = models.AutoField(primary_key = True,editable = False)
    name = models.CharField(max_length=63)
    email = models.EmailField(unique=True,max_length=127)
    password = models.CharField(max_length=63)
    dateCreated = models.DateField(default=datetime.datetime.utcnow,editable=False)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL,blank=True,null=True)

class New(models.Model):
    nid = models.AutoField(primary_key = True,editable = False)
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE)
    headline = models.CharField(max_length=255,blank=True)
    news = models.TextField()
    sentiment = models.FloatField(blank=True,null=True)
    def __str__(self) -> str:
        return f"{self.headline}"
    
class Data(models.Model):
    date = models.DateField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    open = models.FloatField(default=0)
    close = models.FloatField(default=0)
