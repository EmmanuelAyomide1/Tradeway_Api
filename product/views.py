import cloudinary

from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from TradewayBackend.pagination import CustomPagination

from .permissions import IsAdmin
from .models import Category
from .serializers import CategorySerializer,CategoryUpdateSerializer


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