from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.Serializer):
    sid = serializers.IntegerField()
    name = serializers.CharField(max_length=200)

    class Meta:
        model = Stock