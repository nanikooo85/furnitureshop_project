from django.shortcuts import render
# DRF ViewSet და permissions-ის იმპორტი
from rest_framework import generics, viewsets, mixins  # <--- დავამატეთ mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet  # <--- დავამატეთ GenericViewSet
from rest_framework.response import Response  # <--- დავამატეთ Response
from rest_framework import status  # <--- დავამატეთ status

from django_filters.rest_framework import DjangoFilterBackend

# მოდელები
from .models import Category, Product, Cart, Order, CartItem, OrderItem, ProductImage
# სერიალიზატორები
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, OrderSerializer, \
    CartItemSerializer  # <--- დავამატეთ CartItemSerializer-ის იმპორტი


# ----------------------------------------------------
# 1. Category Views (GET /api/categories/ and POST /api/categories/)
# ----------------------------------------------------

# ✅ კორექტირება: ListAPIView შეიცვალა ListCreateAPIView-ით,
# რაც იძლევა POST მოთხოვნის უფლებას (კატეგორიის შესაქმნელად).
class CategoryListAPIView(generics.ListCreateAPIView):
    """ კატეგორიების სიის ჩვენება და ახლის შექმნა """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

class CategoryDetailAPIView(generics.RetrieveAPIView):
    """ კონკრეტული კატეგორიის დეტალების ჩვენება """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'id'

# store/views.py (ჩაანაცვლეთ 2. Product Views მონაკვეთი ამით)

# ----------------------------------------------------
# 2. Product ViewSet (სრული CRUD)
# ----------------------------------------------------

class ProductViewSet(viewsets.ModelViewSet):
    """ პროდუქტების სრული ViewSet-ი (CRUD - GET, POST, PUT, DELETE) """
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'color', 'material']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']

    # ❗ შეგიძლიათ დაამატოთ permission_classes თუ გჭირდებათ კონტროლი,
    # მაგალითად: permission_classes = [IsAdminUser]

# ----------------------------------------------------
# 3. Cart ViewSet (დაცულია) - ჯერ კიდევ სრულყოფილია
# ----------------------------------------------------

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    # ❗ ლოგიკა: აჩვენებს მხოლოდ მიმდინარე მომხმარებლის კალათას
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    # ❗ ლოგიკა: კალათის შექმნისას ავტომატურად ანიჭებს მიმდინარე მომხმარებელს
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ----------------------------------------------------
# 4. Order ViewSet (დაცულია)
# ----------------------------------------------------

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    # ❗ ლოგიკა: აჩვენებს მხოლოდ მიმდინარე მომხმარებლის ორდერებს
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# ----------------------------------------------------
# 5. Cart Item ViewSet (Nested Route) ⭐ ახალი ლოგიკა
# ----------------------------------------------------

class CartItemViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    # ფილტრავს მხოლოდ მიმდინარე კალათის შიგთავსს URL-ის მიხედვით
    def get_queryset(self):
        # cart_pk მოდის Nested Router-იდან (store/urls.py)
        cart_id = self.kwargs.get('cart_pk')
        return CartItem.objects.filter(cart_id=cart_id)

    # ლოგიკა: პროდუქტის დამატება/განახლება
    def perform_create(self, serializer):
        cart_id = self.kwargs.get('cart_pk')
        product_id = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')

        # ვცდილობთ მოვძებნოთ უკვე არსებული CartItem ამ პროდუქტით
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product=product_id)
            # თუ არსებობს, ვზრდით რაოდენობას
            cart_item.quantity += quantity
            cart_item.save()
            # ვაბრუნებთ განახლებულ ობიექტს
            serializer.instance = cart_item
        except CartItem.DoesNotExist:
            # თუ არ არსებობს, ვქმნით ახალ CartItem-ს
            serializer.save(cart_id=cart_id)