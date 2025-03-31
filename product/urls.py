<<<<<<< HEAD
from django.urls import path
from django.urls import include

from rest_framework.routers import DefaultRouter

from .views import ProductReviewViewSet


router = DefaultRouter()
router.register(r'reviews', ProductReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
=======
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
>>>>>>> 11b5a10759c6e66340de98ead7dfe04a0cbe7375
