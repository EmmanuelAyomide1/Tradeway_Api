from django.urls import path
from django.urls import include

from rest_framework.routers import DefaultRouter

from .views import ProductReviewViewSet,CategoryViewSet, OrderListView


router = DefaultRouter()
router.register(r'reviews', ProductReviewViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders', OrderListView.as_view(), name='order-list')
]