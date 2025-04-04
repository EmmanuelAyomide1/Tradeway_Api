from django.contrib import admin

from product.models import Category, Product, ProductImage, Carts, Order


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Carts)
admin.site.register(Order)