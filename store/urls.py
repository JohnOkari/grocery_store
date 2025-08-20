from django.urls import path
from .views import ProductCreateView, AveragePriceView, OrderCreateView, CategoryCreateView, ProductBulkUploadView

urlpatterns = [
    path('products/', ProductCreateView.as_view(), name='product-create'),
    path('products/bulk/', ProductBulkUploadView.as_view(), name='product-bulk-upload'),
    path('average-price/<int:category_id>/', AveragePriceView.as_view(), name='average-price'),
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('categories/', CategoryCreateView.as_view(), name='category-create'),
]