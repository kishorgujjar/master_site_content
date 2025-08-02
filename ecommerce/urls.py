from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Fake admin login (honeypot)
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),

    # Real admin login (hidden)
    path('securelogin/', admin.site.urls),

    # App URL includes
    path('', include('OnlineShoping.urls')),
    path('', include('shop.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('carts.urls')),
    path('orders/', include('orders.urls')),
]

# Serve static/media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
