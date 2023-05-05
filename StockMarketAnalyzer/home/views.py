from datetime import datetime
from typing import Any, Dict
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
import re
from .models import Data, New, Stock, User,Prediction
import plotly.express as px
from django.views.generic.base import TemplateView,RedirectView,View
from .forms import UserCreationForm,UserLoginForm,PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import generics
from django.contrib.auth import login,logout,authenticate,update_session_auth_hash
import feedparser
from pandas import json_normalize
import pandas as pd
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import StockSerializer

FaviconView = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["data"] = {
            "stocks":Stock.objects.all().count(),
            "news":New.objects.all().count(),
            "data":Data.objects.all().count(),
            "users":User.objects.all().count()
        }
        return context

class LogoutView(RedirectView):
    permanent = True
    pattern_name = 'login'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super().get_redirect_url(*args, **kwargs)


class LoginView(TemplateView):
    template_name = "authentication/login.html"

    def post(self, request, *args, **kwargs):
            form1 = UserLoginForm(data=request.POST)
            form2 = UserCreationForm(data=request.POST)
            if form1.is_valid():
                user = authenticate(request,email=request.POST.get("username",""),password=request.POST.get("password",""))
                login(request,user)
                return redirect("/dashboard")
            elif form2.is_valid():
                user = form2.save()
                login(request,user)
                return redirect("/dashboard")
            else:
                return self.render_to_response({"form1":form1,"form2":form2})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/dashboard/")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form1"] = UserLoginForm()
        context["form2"] = UserCreationForm()
        return context

class PasswordChangeView(LoginRequiredMixin,TemplateView):
    template_name = "authentication/passwordchange.html"
    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user)
            return render(request,"authentication/passworddone.html")
        else:
            return self.render_to_response({"form":form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PasswordChangeForm(self.request.user)
        return context

class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard.html"

    login_url = '/login'
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = Stock.objects.all()
        out = []
        for stock in self.request.user.stocks.all():
            data = list(Data.objects.filter(stock__name=stock.name,date__lte=datetime.now().date()).values("date","close","type"))
            predictions = list(Prediction.objects.filter(stock__name=stock.name,date__gt=datetime.now().date()).values("date","close","type"))
            temp = data[-1]
            temp.update({"type":"PREDICTION"})
            dataset = data + [temp] + predictions
            if len(data) != 0:
                graph = px.line(dataset,x="date",y="close",title=stock.name,labels={'x':'Date','y':'Opening'},markers=True,color="type")
                graph.update_layout(title={'font_size':22,'xanchor':'center','x':0.5})
                out.append(graph.to_html())
        context["charts"] = out
        return context

class RssView(View):
    
    def get(self, request, *args, **kwargs):
        mc_rss = feedparser.parse("https://www.moneycontrol.com/rss/latestnews.xml")
        it_rss = feedparser.parse("https://cfo.economictimes.indiatimes.com/rss/topstories")
        ndtv_rss = feedparser.parse("https://feeds.feedburner.com/ndtvnews-latest")
        return JsonResponse(data={"moneycontrol":mc_rss.entries,"indiatimes":it_rss.entries,"ndtv":ndtv_rss.entries})

class AboutUsView(TemplateView):
    template_name = "aboutus.html"

class EditStockView(APIView):

    def get(self,request , *args, **kwargs):
        stock = get_object_or_404(Stock,sid=kwargs.get("id",""))
        if stock in request.user.stocks.all():
            request.user.stocks.remove(stock)
            return Response({"success":True})
        else:
            request.user.stocks.add(stock)
            return Response({"success":True})