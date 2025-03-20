from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    account_type = models.CharField(max_length=255)
    email_verified = models.BooleanField(default=False)
    auth_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

class Carts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    products = models.ForeignKey("Product", on_delete=models.CASCADE)
    buyer_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    def __str__(self):
        return f"Cart {self.id} - {self.user} ({self.created_at})"



class Category(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='product_images/',  blank=True)
    description = models.CharField(max_length=255)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = (models.DateTimeField(auto_now=True))

    def __str__(self):
        return self.name  



class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    categories = models.ManyToManyField(Category)
    size = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    color = models.CharField(max_length=50)
    InitialPrice = models.DecimalField(max_digits=10, decimal_places=2)
    CurrentPrice = models.DecimalField(max_digits=10, decimal_places=2)
    InStock = models.BooleanField(default=True)
    SellerId = models.ForeignKey(Users, on_delete=models.CASCADE)
    images = models.JSONField(default=list)
    video = models.JSONField(default=list)
    IsApproved = models.BooleanField(default=False)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name} - ${self.price}"




class CartProducts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    CartId = models.ForeignKey(Carts, on_delete=models.CASCADE)
    ProductId= models.ForeignKey(Product, on_delete=models.CASCADE)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} in Cart {self.cart.id}"



class Orders(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]



    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ProductId = models.ForeignKey(Product, on_delete=models.CASCADE)
    BuyerId = models.ForeignKey(Users, on_delete=models.CASCADE)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.status} - {self.user}"



class ProductReview(models.Model):
    id = models.BigIntegerField(primary_key=True)
    ProductId = models.ForeignKey(Product, on_delete=models.CASCADE)
    UserId = models.ForeignKey(Users, on_delete=models.CASCADE)
    review = models.CharField(max_length=255)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)