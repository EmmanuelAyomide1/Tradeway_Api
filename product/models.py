import uuid
import cloudinary
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from cloudinary_storage.storage import MediaCloudinaryStorage

from account.models import Account


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to="categories",storage=MediaCloudinaryStorage(), null=True, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = (models.DateTimeField(auto_now=True))

    def __str__(self):
        return self.name  


@receiver(pre_save, sender=Category)
def add_cloudinary_base_url(sender, instance, **kwargs):
    """
    Add Cloudinary base URL to the image before saving
    """
    # Only add base URL if the image is being updated and doesn't already have the base URL
    if instance.pk and instance.image and not str(instance.image).startswith('http'):
        # Get existing instance to check if image changed
        try:
            old_instance = Category.objects.get(pk=instance.pk)
            # If the image has changed, delete the old one from Cloudinary
            if old_instance.image and old_instance.image != instance.image:
                cloudinary.uploader.destroy(old_instance.image.name)
        except Category.DoesNotExist:
            pass

@receiver(pre_delete, sender=Category)
def delete_cloudinary_image(sender, instance, **kwargs):
    """
    Delete image from cloudinary when category is deleted
    """
    if instance.image:
        cloudinary.uploader.destroy(instance.image.name)


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
    video = models.FileField(upload_to="products/",storage=MediaCloudinaryStorage(), blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.name} - ${self.current_price}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.FileField(upload_to="products/",storage=MediaCloudinaryStorage(), blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name}"
        

class Carts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    products = models.ManyToManyField(Product, related_name='carts')
    buyer = models.OneToOneField(Account, on_delete=models.CASCADE)
    def __str__(self):
        return f"Cart {self.id} - {self.buyer} "


class CartProducts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Carts, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} x {self.cart.id}"


class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.status} - {self.buyer.id}"


class ProductReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    review = models.CharField(max_length=255, blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)