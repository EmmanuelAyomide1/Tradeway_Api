import uuid

from django.db import models

from product.models import Order  # Import models from the product app


class Transaction(models.Model):

     STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('successful', 'Successful'),
        ('refunded', 'Refunded'), 
    ]
     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
     reference = models.CharField(max_length=255)
     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)

     def __str__(self):
         return f"Transaction {self.id} - {self.status}"
