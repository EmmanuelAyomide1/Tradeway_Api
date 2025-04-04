import django_filters
from .models import Order


class OrderFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    min_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    status = django_filters.ChoiceFilter(choices=Order.STATUS_CHOICES)
    product_id = django_filters.UUIDFilter(field_name='products__id')
    
    class Meta:
        model = Order
        fields = {
            'id': ['exact'],
            'buyer': ['exact'],
            'address': ['icontains'],
        }