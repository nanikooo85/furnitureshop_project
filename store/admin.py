from django.contrib import admin
from .models import Category, Product, ProductImage, Order, Cart, CartItem, OrderItem

# ინლაინ კლასი ProductImage-ის ჩვენებისთვის Product-ის რედაქტირების გვერდზე
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# Product მოდელის Admin კლასი
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

# Category მოდელის Admin კლასი
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

# OrderItem-ის ინლაინი Order-ის ჩვენებისთვის
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False

# Order მოდელის Admin კლასი
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    readonly_fields = ('total_price', 'created_at', 'updated_at')

# CartItem-ის ინლაინი Cart-ისთვის
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    raw_id_fields = ['product']

# Cart მოდელის Admin კლასი
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    inlines = [CartItemInline]
# Register your models here.
