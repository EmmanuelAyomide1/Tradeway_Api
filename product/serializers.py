from dataclasses import field
from django.db import models

from rest_framework import serializers
from rest_framework import serializers

from .models import CartProducts, Carts, Category, Product, ProductImage, ProductReview, Order, SavedProduct
from .utils import custom_review_handler


class ProductSerializer(serializers.ModelSerializer):

    extra_images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'average_rating',
            'is_approved',
            'seller',
            'in_stock',
            'initial_price',
        ]

    def create(self, validated_data):
        """
        set the initial price to the current price when creating a product
        """
        validated_data['initial_price'] = validated_data['current_price']
        validated_data['seller'] = self.context['request'].user
        product = super().create(validated_data)

        return product

    def get_extra_images(self, obj):
        """
        Retrieve all extra images for the product
        """
        return [{"image": img.image.url, "id": img.id} for img in obj.extra_images.all()]


class ProductDetailSerializer(serializers.ModelSerializer):

    seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_seller(self, obj):
        user = obj.seller
        return {
            "name": user.name,
            "image": None,
            "email": user.email
        }


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a product (fields optional)
    """
    name = serializers.CharField(required=False)  # Optional on update
    description = serializers.CharField(required=False)
    current_price = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2)
    image = serializers.FileField(required=False)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Product
        exclude = [
            'initial_price',
            'is_approved',
            'seller',
            'in_stock',
            'average_rating'
        ]

    def update(self, instance, validated_data):
        """
        set updated product approval to False
        """
        instance.is_approved = False
        return super().update(instance, validated_data)


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for product images
    """
    image = serializers.ImageField(required=True,)

    class Meta:
        model = ProductImage
        fields = '__all__'
        read_only_fields = ['id']

    def create(self, validated_data):
        product = validated_data['product']

        image_count = ProductImage.objects.filter(
            product=product,
        ).count()

        if image_count > 2:
            raise serializers.ValidationError(
                "You can only upload 3 images per product"
            )

        return super().create(validated_data)


class ProductImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ['id', 'product']


class SavedProductSerializer(serializers.ModelSerializer):
    """
    Serializer for saved products
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SavedProduct
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
        depth = 1


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
        fields = '__all__'


class CartsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carts
        fields = '__all__'


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
