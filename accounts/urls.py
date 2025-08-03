from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # path('auth/', views.authView, name='auth'),
    path("", views.registerView, name="register"),
    path("login/", views.loginView, name="login"),
    path('logout/', views.logoutView, name='logout'),
    path('activate/<uidb64>/<token>/', views.activateView, name='activate'),
    path('forgotPassword/', views.forgotPasswordView, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpasswordValidateView, name='resetpassword_validate'),
    path('resetPassword/', views.resetPasswordView, name='resetPassword'),
    path('dashboard/', views.dashboardView, name='dashboard'),

    # dashboard
    path('my_orders/', views.myOrdersView, name='my_orders'),
    path('order_tracking/', views.dashboardOrderTracking, name='order_tracking'),
    path('payment_details/', views.dashboardPaymentDetail, name='payment_details'),
    path('user_details/', views.dashboardUserDetails, name='user_details'),
    path('edit_profile/', views.editProfile, name='edit_profile'),
    path('change_password/', views.changePassword, name='change_password'),
    path('order_detail/<int:order_id>/', views.orderDetails, name='order_detail'),


]