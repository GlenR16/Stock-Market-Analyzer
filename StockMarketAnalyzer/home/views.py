from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
import re
from .models import Data, New, Stock, User
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

FaviconView = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

class IndexView(TemplateView):
    template_name = "index.html"

class LogoutView(RedirectView):
    permanent = True
    pattern_name = 'login'

    def get_redirect_url(self, *args, **kwargs):
        logout(self.request)
        return super().get_redirect_url(*args, **kwargs)


class SignupView(TemplateView):
    template_name = "authentication/signup.html"

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect("/dashboard")
        else:
            return self.render_to_response({"form":form})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/dashboard/")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = UserCreationForm()
        return context

class LoginView(TemplateView):
    template_name = "authentication/login.html"

    def post(self, request, *args, **kwargs):
            form = UserLoginForm(data=request.POST)
            if form.is_valid():
                user = authenticate(request,email=request.POST.get("username",""),password=request.POST.get("password",""))
                login(request,user)
                return redirect("/dashboard/")
            else:
                return self.render_to_response({"form":form})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/dashboard/")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = UserLoginForm()
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
        data = Data.objects.filter(stock__name="TCS")
        graph = px.line(x=[i.date for i in data],y=[i.open for i in data],title="TCS",labels={'x':'Date','y':'Opening'})
        graph.update_layout(title={'font_size':22,'xanchor':'center','x':0.5})
        context["chart"] = graph.to_html()
        return context

class RssView(View):
    
    def get(self, request, *args, **kwargs):
        mc_rss = feedparser.parse("https://www.moneycontrol.com/rss/latestnews.xml")
        it_rss = feedparser.parse("https://cfo.economictimes.indiatimes.com/rss/topstories")
        ndtv_rss = feedparser.parse("https://feeds.feedburner.com/ndtvnews-latest")
        return JsonResponse(data={"moneycontrol":mc_rss.entries,"indiatimes":it_rss.entries,"ndtv":ndtv_rss.entries})

class AboutUsView(TemplateView):
    template_name = "aboutus.html"


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

