from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.homeView, name="home"),
    # path("priceFilter/", views.priceFilterView, name="priceFilter"),
    
    
    path("contact/", views.contactView, name="contact"),
    path("search/", views.searchView, name="search"),

]