from django.contrib import admin

from product.models import Category, Product, ProductImage


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Category)