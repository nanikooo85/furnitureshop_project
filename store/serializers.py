from rest_framework import serializers
from decimal import Decimal
# აუცილებელი მოდელები
from .models import Category, Product, ProductImage, Cart, Order, CartItem, OrderItem
# CustomUser-ის იმპორტი Cart/Order სერიალიზაციისთვის
from users.models import CustomUser


# ----------------------------------------------------
# 1. Product Image Serializer (For Product Gallery)
# ----------------------------------------------------

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']


# ----------------------------------------------------
# 2. Product Serializer
# ----------------------------------------------------

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True, source='productimage_set')
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 'description', 'price', 'stock',
            'is_available', 'featured', 'color', 'material', 'images', 'created_at', 'updated_at',
        ]


# ----------------------------------------------------
# 3. Category Serializer
# ----------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'is_active', 'created_at'
        ]


# ----------------------------------------------------
# 4. Cart Item Serializer
# ----------------------------------------------------

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total_item_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_item_price']

    def get_total_item_price(self, item: CartItem):
        return item.product.price * item.quantity


# ----------------------------------------------------
# 5. Cart Serializer
# ----------------------------------------------------

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_cart_price']
        read_only_fields = ['user']

    def get_total_cart_price(self, cart: Cart):
        items = cart.items.all()
        total = sum(item.product.price * item.quantity for item in items)
        return total


# ----------------------------------------------------
# 6. Order Serializer: Order Item Detail (price ველის კორექტირება)
# ----------------------------------------------------

class OrderItemSerializer(serializers.ModelSerializer):
    """
    სერიალიზატორი OrderItem-ისთვის: გამოიყენება OrderSerializer-ის შიგნით
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    # ✅ product_price იღებს მნიშვნელობას price ველიდან
    product_price = serializers.DecimalField(source='price', max_digits=10, decimal_places=2,
                                             read_only=True)

    total_item_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_item_price']
        read_only_fields = ['product', 'product_name', 'product_price']

    def get_total_item_price(self, item: OrderItem):
        # ✅ იყენებს item.price-ს
        return item.price * item.quantity


# ----------------------------------------------------
# 7. Order Serializer: Main (created_at და status ველების კორექტირება)
# ----------------------------------------------------

class OrderSerializer(serializers.ModelSerializer):
    """
    მთავარი სერიალიზატორი Order-ისთვის (Order History)
    """
    items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        # ✅ created_at და status ველები გამოიყენება
        fields = ['id', 'user_username', 'created_at', 'status', 'total_price', 'items']
        read_only_fields = ['created_at', 'total_price']