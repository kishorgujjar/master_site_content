from django.urls import path

from . import views


urlpatterns = [
    path("shop/", views.shopView, name="shop"),
    path('product/detail/<int:product_id>/', views.productDetailView, name='product_detail'),    
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('search/', views.searchView, name='search'),  # name + description search
    path('search-by-name/', views.searchByNameView, name='search_by_name'),  # name-only search
    
]
