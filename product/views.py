from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Count
from .models import ProductReview, Product
from .serializers import ProductReviewSerializer
from .utils import IsReviewOwnerOrAdminPermission

class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsReviewOwnerOrAdminPermission]
    
    def get_queryset(self):
        queryset = ProductReview.objects.all()
        
       
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        

        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Sorting
        sort = self.request.query_params.get('sort', 'newest')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort == 'popular':
            queryset = queryset.annotate(
                review_count=Count('id')
            ).order_by('-review_count')
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
     
        product_id = request.query_params.get('product_id')
        total_reviews = queryset.count() if product_id else 0
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'total_reviews': total_reviews,
                'reviews': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'total_reviews': total_reviews,
            'reviews': serializer.data
        })