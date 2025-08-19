from rest_framework import serializers
from .models import Category, Product, Order
from typing import Any, cast
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category']

class OrderSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=cast(Any, Product.objects).all())
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Order
        fields = ['id', 'products', 'total', 'created_at', 'customer']

    def create(self, validated_data):
        products = validated_data.pop('products')
        order = cast(Any, Order.objects).create(**validated_data)
        order.products.set(products)
        order.total = sum(p.price for p in products)
        order.save()
        return order