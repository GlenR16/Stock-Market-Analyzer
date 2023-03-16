

import subprocess
from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
import re
from django.core import serializers
from .models import Data, New, Stock, User

def index(request):
    if request.method == 'POST':
        request.session.flush()
    return render(request,'index.html')

emailre = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        if (email!='' and username!='' and password!='' and re.fullmatch(emailre, email) and not User.objects.filter(email=email)):
            new_user = User(email=email,name=username,password=password)
            new_user.save()
            request.session['email'] = new_user.email
            return redirect(home)
        else:
            return render(request,'signup.html',{'error':True})
    else:
        session = session_verification(request)
        if session!='':
            return redirect(home)
        else:
            return render(request,'signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            curr_user = User.objects.get(email=email)
        except:
            curr_user = ''
        if (curr_user!='' and password==curr_user.password):
            request.session['email'] = curr_user.email
            return redirect(home)
        else:
            return render(request,'login.html',{'error':True})
    else:
        session = session_verification(request)
        if session!='':
            return redirect(home)
        else:
            return render(request,'login.html')

def home(request):
    session = session_verification(request)
    if session!='':
        curr_user = User.objects.get(email=session)
        stock_list = Stock.objects.all()
        if request.method == 'POST':
            stockid = int(request.POST['stockid'])
            if stockid!='' and type(stockid) == int:
                try:
                    curr_user.stock = stock_list[stockid-1]
                    curr_user.save()
                except Exception as e:
                    print("Error for: ",stockid,e)
            return HttpResponseRedirect('/home/')
        try:
            curr_stock = Stock.objects.get(sid=curr_user.stock.sid)
            curr_news = New.objects.filter(stock=curr_stock)
            history = Data.objects.filter(stock=curr_stock)
            return render(request,"home.html",{'user':curr_user,'stock':curr_stock,'news':curr_news,'history':history,'list':stock_list})
        except:
            return render(request,"home.html",{'user':curr_user,'list':stock_list})
    else:
        return redirect(login)
    
def session_verification(request):
    try:
        session = request.session['email']
    except:
        session = ''
    return session

def aboutus(request):
    return render(request,"aboutus.html")

def api(request):
    session = session_verification(request)
    if session!='':
        curr_user = User.objects.get(email=session)
        curr_stock = Stock.objects.all().get(sid=curr_user.stock.sid)
        history = Data.objects.filter(stock=curr_stock.sid)
        data =  serializers.serialize('json',[curr_stock])+serializers.serialize('json', history)
        return HttpResponse(data, content_type="json")
    else:
        return HttpResponse("User not logged in.")

