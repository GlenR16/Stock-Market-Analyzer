from django.contrib import admin
from .models import User,Stock,New,Data

# Register your models here.

@admin.register(New)
class NewAdmin(admin.ModelAdmin):
    list_display = ("headline","sentiment","stock","date")
    list_filter = ("stock",)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("name","code")

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name","email",)

@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ("stock","date","open","close","high","low","volume")
    list_filter = ("stock",)
