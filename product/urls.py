from django.urls import path
from django.urls import include

from rest_framework.routers import DefaultRouter

from .views import CartViewset, ProductReviewViewSet, CategoryViewSet


router = DefaultRouter()
router.register(r'reviews', ProductReviewViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'carts', CartViewset)

urlpatterns = [
    path('', include(router.urls)),
]
