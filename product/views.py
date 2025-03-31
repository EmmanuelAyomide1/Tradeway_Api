import cloudinary

from django.db.models import Count

from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny

from TradewayBackend.pagination import CustomPagination

from .models import Category,ProductReview, Product
from .permissions import IsAdmin
from .serializers import (
    CategorySerializer,
    CategoryUpdateSerializer, 
    ProductReviewSerializer, 
    ProductReviewListSerializer
    )
from .utils import IsReviewOwnerOrAdminPermission


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories
    """
    queryset = Category.objects.all().order_by('-created_at')
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    parser_classes = [MultiPartParser, FormParser]
    search_fields = ['name']
    serializer_class = CategorySerializer

    def get_permissions(self):
        """
        Return permissions based on action:
        - List and retrieve: allow all users
        - Create, update, delete: admin only
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CategoryUpdateSerializer  
        return super().get_serializer_class()
        
    def update(self, request, *args, **kwargs):
        """
        Update a category (admin only)
        """
        instance = self.get_object()
        old_image = instance.image
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # If image is being updated, delete the old image from Cloudinary
        if old_image and 'image' in request.data and old_image != request.data['image']:
            try:
                cloudinary.uploader.destroy(old_image.name)
            except Exception as e:
                # Log error but continue with update
                print(f"Error deleting old image: {e}")
        
        self.perform_update(serializer)
        return Response(serializer.data)


class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsReviewOwnerOrAdminPermission]
    queryset = ProductReview.objects.all()
    pagination_class = CustomPagination
    
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
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ProductReviewListSerializer
        return super().get_serializer_class()