from django.urls import path

from . import views


urlpatterns = [
    path("shop/", views.shopView, name="shop"),
    path('product/detail/<int:product_id>/', views.productDetailView, name='product_detail'),    
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]
