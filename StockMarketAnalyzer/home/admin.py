from django.contrib import admin
from .models import Users,Stocks,News,History

# Register your models here.
admin.site.register(Users)
admin.site.register(Stocks)
admin.site.register(News)
admin.site.register(History)
