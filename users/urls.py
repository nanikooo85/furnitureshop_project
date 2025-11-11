# users/urls.py - სრულიად სწორი შიგთავსი (Router-ის გარეშე)

from django.urls import path
from . import views

urlpatterns = [
    # POST /api/register/
    path('register/', views.RegisterAPIView.as_view(), name='user-register'),

    # POST /api/login/
    path('login/', views.LoginAPIView.as_view(), name='user-login'),
]