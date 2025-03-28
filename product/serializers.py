from rest_framework import serializers
from .models import Users, CartProducts, Carts, Category, Product, ProductReview, Orders


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
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
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new category
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        if not attrs.get('name'):
            raise serializers.ValidationError({'name': 'Name is required'})
        if not attrs.get('description'):
            raise serializers.ValidationError({'description': 'Description is required'})
        if not attrs.get('image'):
            raise serializers.ValidationError({'image': 'Image is required'})
        return attrs

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
        model = Orders
        fields = '__all__' 