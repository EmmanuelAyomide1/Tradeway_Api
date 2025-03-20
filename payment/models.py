from django.db import models
from product.models import Order, Cart  # Import models from the product app
import uuid


class Transactions(models.Model):

     STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('successful', 'Successful'),
        ('refunded', 'Refunded'), 
    ]
     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
     reference = models.CharField(max_length=255)
     OrderId = models.ForeignKey(Order, on_delete=models.CASCADE)
     CreatedAt = models.DateTimeField(auto_now_add=True)
     UpdatedAt = models.DateTimeField(auto_now=True)

     def __str__(self):
         return f"Transaction {self.transaction_id} - {self.amount} - {self.status}"
