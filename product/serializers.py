from django.db import models
from django.conf import settings

from rest_framework import serializers

from .models import Cart, CartProduct, Category, Product, ProductReview, Order
from .utils import custom_review_handler


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
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


class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'


class OrderListSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'


class CartProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = '__all__'


class CategoryUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a category (fields optional)
    """
    name = serializers.CharField(required=False)  # Optional on update
    description = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Category
        fields = '__all__'


class CartProductSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=True)

    class Meta:
        model = CartProduct
        exclude = ['cart']
        depth = 1

    def create(self, validated_data):
        cart, created = Cart.objects.get_or_create(
            buyer=self.context['request'].user)
        validated_data['cart'] = cart
        return super().create(validated_data)

    def to_representation(self, instance):
        # Custom representation to include product details
        product_data = ProductSerializer(instance.product).data
        cart_product_data = super().to_representation(instance)
        cart_product_data['product'] = product_data
        return cart_product_data


class ProductReviewSerializer(serializers.ModelSerializer):
    is_offensive = serializers.BooleanField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ProductReview
        fields = [
            'id',
            'user',
            'product',
            'rating',
            'comment',
            'is_offensive',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['is_offensive', 'created_at', 'updated_at']

    def validate(self, data):

        if custom_review_handler.filter_bad_words(data.get('comment', '')):
            data['is_offensive'] = True

        return data

    def create(self, validated_data):

        user = validated_data['user']
        product = validated_data['product']

        has_purchased = Order.objects.filter(
            buyer=user,
            products=product,
            status='delivered'
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError(
                "You can only review products you have purchased"
            )

        review = super().create(validated_data)
        self._update_product_rating(product)

        return review

    def update(self, instance, validated_data):
        # Update review and recalculate rating if needed
        original_rating = instance.rating
        updated_review = super().update(instance, validated_data)

        if original_rating != updated_review.rating:
            self._update_product_rating(updated_review.product)

        return updated_review

    def _update_product_rating(self, product):
        # Recalculate average rating
        avg_rating = ProductReview.objects.filter(
            product=product
        ).aggregate(models.Avg('rating'))['rating__avg'] or 0

        product.average_rating = round(avg_rating, 2)
        product.save()


class ProductReviewListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user')

    class Meta:
        model = ProductReview
        fields = '__all__'

    def get_user(self, obj):
        return {
            "name": obj.user.name,
            "image": None,
            "email": obj.user.email,
        }


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
