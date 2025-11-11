from django.shortcuts import render
# DRF ViewSet და permissions-ის იმპორტი
from rest_framework import generics, viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated  # <--- აუცილებელი იმპორტი დაცვისთვის
from django_filters.rest_framework import DjangoFilterBackend

# მოდელები
from .models import Category, Product, Cart, Order, CartItem, OrderItem, ProductImage
# სერიალიზატორები
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, OrderSerializer


# ----------------------------------------------------
# 1. Category Views (GET /api/categories/ and /api/categories/<id>/)
# ----------------------------------------------------

class CategoryListAPIView(generics.ListAPIView):
    """
    კატეგორიების სიის ჩვენება (GET /api/categories/)
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class CategoryDetailAPIView(generics.RetrieveAPIView):
    """
    კონკრეტული კატეგორიის დეტალების ჩვენება (GET /api/categories/<id>/)
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'id'


# ----------------------------------------------------
# 2. Product Views (GET /api/products/ and /api/products/<id>/)
# ----------------------------------------------------

class ProductListAPIView(generics.ListAPIView):
    """
    პროდუქტების სიის ჩვენება, ფილტრაციის შესაძლებლობით (GET /api/products/)
    """
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'color', 'material']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    კონკრეტული პროდუქტის დეტალების ჩვენება (GET /api/products/<id>/)
    """
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    lookup_field = 'id'


# ----------------------------------------------------
# 3. Cart ViewSet (დაცულია)
# ----------------------------------------------------

class CartViewSet(viewsets.ModelViewSet):
    # ⭐⭐⭐ დაცვა: მხოლოდ ავტორიზებულ მომხმარებელს შეუძლია წვდომა ⭐⭐⭐
    permission_classes = [IsAuthenticated]

    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    # აქ დავამატებთ ლოგიკას, რომ მხოლოდ მიმდინარე მომხმარებლის კალათა გამოჩნდეს,
    # მაგრამ ჯერ ტესტირებაა საჭირო.


# ----------------------------------------------------
# 4. Order ViewSet (დაცულია)
# ----------------------------------------------------

class OrderViewSet(viewsets.ModelViewSet):
    # ⭐⭐⭐ დაცვა: მხოლოდ ავტორიზებულ მომხმარებელს შეუძლია წვდომა ⭐⭐⭐
    permission_classes = [IsAuthenticated]

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # აქაც დავამატებთ ლოგიკას, რომ მხოლოდ მიმდინარე მომხმარებლის ორდერები გამოჩნდეს.