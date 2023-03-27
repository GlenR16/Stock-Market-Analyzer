import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from .managers import UserManager

class Stock(models.Model):
    sid = models.AutoField(primary_key = True,editable = False)
    name = models.CharField(max_length=63)
    code = models.CharField(unique=True,max_length=20)
    def __str__(self) -> str:
        return f"{self.name}"

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email Address",unique=True,max_length=127)
    name = models.CharField(max_length=255)

    stocks = models.ManyToManyField(Stock, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

class New(models.Model):
    nid = models.AutoField(primary_key = True,editable = False)
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE)
    headline = models.CharField(max_length=255,blank=True)
    news = models.TextField()
    sentiment = models.FloatField(blank=True,null=True)
    date = models.DateField()
    
    def __str__(self) -> str:
        return f"{self.date}"
    
class Data(models.Model):
    date = models.DateField()
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    open = models.FloatField(default=0,blank=True,null=True)
    close = models.FloatField(default=0)
