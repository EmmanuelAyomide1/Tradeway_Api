from django.shortcuts import get_object_or_404
import cloudinary
from django.db.models import Q
from rest_framework import status, viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from TradewayBackend.pagination import CustomPagination
from .permissions import IsAdmin
from .models import Category
from .serializers import CategorySerializer, CategoryCreateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories
    """
    queryset = Category.objects.all().order_by('-created_at')
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

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
        """
        Return different serializers based on action
        """
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateSerializer
        return CategorySerializer

    def list(self, request, *args, **kwargs):
        """
        List categories with optional filtering by name
        """
        queryset = self.get_queryset()
        name_filter = request.query_params.get('name', None)
        
        if name_filter:
            queryset = queryset.filter(Q(name__icontains=name_filter))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new category (admin only)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
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
        
    def destroy(self, request, *args, **kwargs):
        """
        Delete a category (admin only)
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
