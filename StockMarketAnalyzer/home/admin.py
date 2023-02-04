from django.contrib import admin
from .models import User,Stock,New,History

# Register your models here.

@admin.register(New)
class NewAdmin(admin.ModelAdmin):
    list_display = ("stock","headline","sentiment",)
    list_filter = ("stock",)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("stock_name","close","predicted_close",)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name","email",)

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("stock","date",)