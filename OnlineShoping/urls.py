from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.homeView, name="home"),
    path("shop/", views.shopView, name="shop"),
    # path("priceFilter/", views.priceFilterView, name="priceFilter"),
    
    path("checkout/", views.checkoutView, name="checkout"),
    path("contact/", views.contactView, name="contact"),
    path('product/detail/<int:product_id>/', views.productDetailView, name='product_detail'),    
    path("search/", views.searchView, name="search"),

]