from django.shortcuts import render
from rest_framework import generics, viewsets, mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction  # ✅ აუცილებელი იმპორტი Order-ის ლოგიკისთვის
from decimal import Decimal  # ✅ აუცილებელი იმპორტი ფასის კალკულაციისთვის

# მოდელები
from .models import Category, Product, Cart, Order, CartItem, OrderItem, ProductImage
# სერიალიზატორები
from .serializers import CategorySerializer, ProductSerializer, CartSerializer, OrderSerializer, \
    CartItemSerializer  # ✅ OrderItemSerializer-ის იმპორტი Order-ის გამოტანისთვის


# ----------------------------------------------------
# 1. Category Views (ListCreateAPIView, RetrieveAPIView)
# ----------------------------------------------------

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


# ----------------------------------------------------
# 3. Cart ViewSet (დაცულია)
# ----------------------------------------------------

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ----------------------------------------------------
# 4. Order ViewSet (შეკვეთის შექმნის ლოგიკა) ✅ გამოსწორებულია!
# ----------------------------------------------------

class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):  # ვიყენებთ GenericViewSet + mixins-ს, რადგან Update/Delete არ გვჭირდება
    """
    მართავს შეკვეთებს: List, Retrieve, Create (კალათიდან)
    """
    queryset = Order.objects.select_related('user').prefetch_related('items__product').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """ფილტრი: მომხმარებელს შეუძლია მხოლოდ საკუთარი შეკვეთების ნახვა"""
        user = self.request.user
        return Order.objects.filter(user=user).select_related('user').prefetch_related('items__product')

    def create(self, request, *args, **kwargs):
        """
        ქმნის შეკვეთას მომხმარებლის ამჟამინდელი კალათის საფუძველზე.
        """
        user = request.user

        # 1. მომხმარებლის კალათის მიღება
        try:
            cart = Cart.objects.prefetch_related('items__product').get(user=user)
        except Cart.DoesNotExist:
            return Response({"error": "კალათა ვერ მოიძებნა."},
                            status=status.HTTP_404_NOT_FOUND)

        # 2. კალათაში არსებული ნივთების შემოწმება
        if not cart.items.exists():
            return Response({"error": "კალათა ცარიელია, შეკვეთა ვერ შეიქმნება."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 3. ტრანზაქციის დაწყება (თუ რამე შეცდომა მოხდა, ყველაფერი უკან დაბრუნდება)
        with transaction.atomic():
            # store/views.py - OrderViewSet-ის create მეთოდში (სწორი ვერსია)

            # 4. შეკვეთის შექმნა (ჩავანაცვლეთ payment_status-ით status)
            order = Order.objects.create(user=user, status='P')

            order_items = []
            total_price = Decimal(0)

            for item in cart.items.all():
                # 5. OrderItem-ის შექმნა CartItem-ის საფუძველზე
                order_item = OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price  # ✅ unit_price ჩანაცვლდა price-ით
                )
                order_items.append(order_item)

                # 6. მთლიანი ფასის გამოთვლა
                total_price += item.product.price * item.quantity

                # 7. (მარაგის განახლება) - ეს ლოგიკა ჯერ გათიშულია

            # 8. OrderItem-ების მასიური შენახვა
            OrderItem.objects.bulk_create(order_items)

            # 9. Order-ის მთლიანი ფასის და სტატუსის განახლება
            order.total_price = total_price
            order.save()

            # 10. კალათის დაცლა
            cart.items.all().delete()

            # 11. პასუხის დაბრუნება
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ----------------------------------------------------
# 5. Cart Item ViewSet (Nested Route)
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