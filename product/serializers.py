from django.conf import settings
from rest_framework import serializers
from .models import CartProducts, Carts, Category, Product, ProductReview, Order


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = '__all__' 


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__' 


class CartProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProducts
        fields = '__all__' 


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model
    """
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    image = serializers.ImageField(required=True) 

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategoryUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a category (fields optional)
    """
    name = serializers.CharField(required=False)  # Optional on update
    description = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Category
        fields = "__all__"


class CartsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carts
        fields = '__all__' 


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__' 


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__' 