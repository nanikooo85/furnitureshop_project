from rest_framework import serializers
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
# 2. Product Serializer (გამოსწორებულია Category-ის შექმნის ლოგიკა)
# ----------------------------------------------------

class ProductSerializer(serializers.ModelSerializer):
    # იმიჯების წაკითხვა
    images = ProductImageSerializer(many=True, read_only=True, source='productimage_set')

    # ✅ კორექტირება 1: Category-ის ID-ის მიღება POST/PUT-ისთვის (ჩაწერა)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    # ✅ კორექტირება 2: Category-ის სახელის გამოჩენა GET-ისთვის (წაკითხვა)
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
# 4. Cart Item Serializer (აუცილებელია Cart-ის შიგთავსისთვის)
# ----------------------------------------------------

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    # ველის გამოთვლა: ფასი * რაოდენობა
    total_item_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        # product (ID) და quantity საჭიროა POST/PUT მოთხოვნებისთვის
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_item_price']

    def get_total_item_price(self, item: CartItem):
        # გამოთვლის ფასი * რაოდენობა
        return item.product.price * item.quantity


# ----------------------------------------------------
# 5. Cart Serializer (ახლა მუშაობს)
# ----------------------------------------------------

class CartSerializer(serializers.ModelSerializer):
    # Items-ის წაკითხვა
    items = CartItemSerializer(many=True, read_only=True)

    # ველის გამოთვლა: კალათის მთლიანი ღირებულება
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_cart_price']
        read_only_fields = ['user']

    def get_total_cart_price(self, cart: Cart):
        # გამოიყენება cart.items.all()
        items = cart.items.all()

        # კალათის ყველა ელემენტის ფასის შეჯამება
        total = sum(item.product.price * item.quantity for item in items)
        return total


# ----------------------------------------------------
# 6. Order Serializer
# ----------------------------------------------------
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'created_at']
        read_only_fields = ['user', 'total_price', 'status']