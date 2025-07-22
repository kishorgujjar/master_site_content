from django.urls import path

from . import views

urlpatterns = [
    # path('auth/', views.authView, name='auth'),
    path("register/", views.registerView, name="register"),
    path("login/", views.loginView, name="login"),
    path('logout/', views.logoutView, name='logout'),
    path('activate/<uidb64>/<token>/', views.activateView, name='activate'),
    path('forgotPassword/', views.forgotPasswordView, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpasswordValidateView, name='resetpassword_validate'),
    path('resetPassword/', views.resetPasswordView, name='resetPassword'),
    path('dashboard/', views.dashboardView, name='dashboard')

]