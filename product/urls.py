from django.urls import path
from django.urls import include

from rest_framework.routers import DefaultRouter

from .views import ProductReviewViewSet


router = DefaultRouter()
router.register(r'reviews', ProductReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
