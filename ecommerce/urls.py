from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", include("OnlineShoping.urls")),
    path("", include("shop.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("carts.urls")),
    path("orders/", include("orders.urls")),

    path("admin/", admin.site.urls),
]
# Serve static & media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)