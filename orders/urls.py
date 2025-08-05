from django.urls import include, path

from . import views

urlpatterns = [
    path('place_order/', views.placeOrderView, name='place_order'),
    path('payments/', views.paymentsView, name='payments'),
    path('success/', views.paymentSuccessView, name='success'),

]