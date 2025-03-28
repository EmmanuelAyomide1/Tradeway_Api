from django.urls import path
from .views import (
  ProductReviewViewSet
  )


urlpatterns = [
     path("productreview/", ProductReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name="productreview"),   
]   