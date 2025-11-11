from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Endpoints-ის ჩართვა. ყველა მისამართი დაიწყება /api/
    # 1. store Endpoints (პროდუქტები, კატეგორიები)
    path('api/', include('store.urls')),

    # 2. users Endpoints (რეგისტრაცია, ავტორიზაცია)
    path('api/', include('users.urls')),
]

# მედია ფაილების (სურათების) URL-ების კონფიგურაცია development-ისთვის
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)