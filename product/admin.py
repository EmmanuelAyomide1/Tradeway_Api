from django.contrib import admin

from product.models import Category, Product, ProductImage, Cart, Order


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Order)
