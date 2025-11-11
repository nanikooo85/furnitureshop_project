# store/urls.py - ფინალური, გამოსწორებული ვერსია (ამოღებულია /api/ დუბლირება)

from django.urls import path, include
# ✅ import-ს დავუმატეთ SimpleRouter და NestedDefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter, SimpleRouter
from . import views

# 1. მთავარი Router-ის ინიციალიზაცია
router = SimpleRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')

# 2. Nested Router-ის ინიციალიზაცია Cart-ისთვის
# ეს ქმნის ლოგიკურ მისამართს /carts/{cart_pk}/items/
carts_router = NestedDefaultRouter(router, r'carts', lookup='cart')
carts_router.register(r'items', views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    # 1. მთავარი Router-ის URL-ების დამატება (წაიშალა 'api/')
    path('', include(router.urls)),

    # 2. Nested Router-ის URL-ების დამატება (წაიშალა 'api/')
    path('', include(carts_router.urls)),

    # 3. Category URL-ები (წაიშალა 'api/')
    path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<int:id>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),
]