from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('shop/', include('products.urls')),
    path('', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('account/', include('accounts.urls')),
    path('campaigns/', include('campaigns.urls')),  # <-- ADD THIS LINE
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
