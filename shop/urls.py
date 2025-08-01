from django.urls import path

from . import views


urlpatterns = [
    # path("shop/", views.shopView, name="shop"),
    # path('product/detail/<int:shop_id>/', views.detailView, name='product_detail'),
    # path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='products_by_category'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]
