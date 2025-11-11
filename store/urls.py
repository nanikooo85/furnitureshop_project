# store/urls.py - სრული, გამართული კოდი

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router-ის ინიციალიზაცია
router = DefaultRouter()
# ViewSet-ების რეგისტრაცია: ეს ქმნის მისამართებს /api/carts/ და /api/orders/
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    # 1. Router-ის URL-ების დამატება (აუცილებელია ViewSets-ებისთვის)
    path('', include(router.urls)),

    # 2. Category/Product URL-ები (List/Detail Views)
    path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<int:id>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),

    path('products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:id>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
]