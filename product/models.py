import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from cloudinary_storage.storage import MediaCloudinaryStorage

from account.models import Account
from django.conf import settings


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(
        upload_to="categories", storage=MediaCloudinaryStorage(), null=True, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = (models.DateTimeField(auto_now=True))

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    categories = models.ManyToManyField(Category, related_name='product')
    size = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=255)
    color = models.CharField(max_length=50, null=True, blank=True)
    initial_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    seller = models.ForeignKey(Account, on_delete=models.CASCADE)
    video = models.FileField(
        upload_to="products/", storage=MediaCloudinaryStorage(), blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.name} - ${self.current_price}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name='images', on_delete=models.CASCADE)
    image = models.FileField(
        upload_to="products/", storage=MediaCloudinaryStorage(), blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    products = models.ManyToManyField(
        Product, through='CartProduct')
    buyer = models.OneToOneField(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart {self.id} - {self.buyer} "


class CartProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="cart_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.product.name} x {self.cart.id}"


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    products = models.ManyToManyField(Product, related_name='orders')
    buyer = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    total_amount = models.PositiveIntegerField(default=0)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order {self.status} - {self.buyer.name}"


class ProductReview(models.Model):

    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    is_offensive = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'product']
