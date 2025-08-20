from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, Product, Order
from .serializers import ProductSerializer, OrderSerializer, CategorySerializer
from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist
from typing import cast, Any
import csv
import io
from django.contrib.auth.models import User
from django.conf import settings
from importlib import import_module

def _send_admin_email(subject: str, message: str) -> bool:
    try:
        notifications = import_module('store.notifications')
        return bool(getattr(notifications, 'send_admin_order_email')(subject=subject, message=message))
    except Exception:
        return False

def _send_customer_sms(phone_number: str, message: str) -> bool:
    try:
        notifications = import_module('store.notifications')
        return bool(getattr(notifications, 'send_sms_via_africastalking')(phone_number=phone_number, message=message))
    except Exception:
        return False

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # Permission: IsAuthenticated (default)

class AveragePriceView(APIView):
    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            # Get all descendant products (recursive hierarchy)
            descendants = category.get_descendants(include_self=True)
            products = Product.objects.filter(category__in=descendants)
            avg_price = products.aggregate(Avg('price'))['price__avg'] or 0
            return Response({'average_price': avg_price})
        except ObjectDoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # Ensures customer is set to authenticated user
    def perform_create(self, serializer):
        order = cast(Order, serializer.save())
        # Build email content
        products_qs = cast(Any, order.products).all()
        product_lines = [f"- {p.name} (Ksh {p.price})" for p in products_qs]
        text_body = (
            f"New order #{order.pk}\n"
            f"Customer: {cast(Any, order.customer).username} (id {cast(Any, order).customer_id})\n"
            f"Total: Ksh {order.total}\n"
            f"Items:\n" + "\n".join(product_lines)
        )
        _send_admin_email(subject=f"New order #{order.pk}", message=text_body)

        # Send SMS to customer if they have a phone number stored in profile
        phone_number = getattr(order.customer, 'phone_number', None)
        if not phone_number:
            phone_number = getattr(settings, 'TEST_CUSTOMER_PHONE', None)
        if phone_number:
            _send_customer_sms(
                phone_number=str(phone_number),
                message=f"Your order #{order.pk} was received. Total: Ksh {order.total}.",
            )

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductBulkUploadView(APIView):
    def post(self, request):
        created_ids = []
        errors = []

        rows = []
        if 'file' in request.FILES:
            try:
                content = request.FILES['file'].read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(content))
                rows = list(reader)
            except Exception as exc:
                return Response({'error': f'Invalid file: {exc}'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            rows = request.data.get('products') or []
            if not isinstance(rows, list):
                return Response({'error': 'Provide a CSV file under "file" or a JSON list under "products"'}, status=status.HTTP_400_BAD_REQUEST)

        for index, item in enumerate(rows, start=1):
            name = (item.get('name') or '').strip()
            price = item.get('price')
            category_id = item.get('category') or item.get('category_id')
            category_name = item.get('category_name')

            if not name or price is None:
                errors.append({'row': index, 'error': 'Missing name or price'})
                continue

            category_instance = None
            if category_id:
                try:
                    category_instance = Category.objects.get(pk=category_id)
                except ObjectDoesNotExist:
                    errors.append({'row': index, 'error': f'Category id {category_id} not found'})
                    continue
            elif category_name:
                category_instance, _ = Category.objects.get_or_create(name=category_name, defaults={'parent': None})
            else:
                errors.append({'row': index, 'error': 'Category is required (category_id or category_name)'})
                continue

            serializer = ProductSerializer(data={'name': name, 'price': price, 'category': category_instance.pk})
            if serializer.is_valid():
                product = cast(Product, serializer.save())
                product_id = int(cast(Any, product).pk)
                created_ids.append(product_id)
            else:
                errors.append({'row': index, 'error': serializer.errors})

        status_code = status.HTTP_201_CREATED if created_ids else status.HTTP_400_BAD_REQUEST
        return Response({'created': len(created_ids), 'product_ids': created_ids, 'errors': errors}, status=status_code)
