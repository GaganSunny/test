from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('signup/', view=views.signup, name='signup'),
    path('services/', views.services, name='services'),
    path('service-product/', views.service_product, name='service_product'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('order-success/', views.order_success, name='order_success'),
    path('create-order/', views.create_order, name='create_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('admin-dashbord/', views.admin_dashbord, name='admin_dashbord'),
    path('service-provider/dashboard/', views.service_provider_dashboard, name='service_provider_dashboard'),
    path('cancel-order/<int:order_id>/', views.cancel_order_by_admin, name='cancel_order_by_admin'),
    path('service-provider/order/<int:order_id>/accept/', views.accept_order, name='accept_order'),
    path('service-provider/order/<int:order_id>/reject/', views.reject_order, name='reject_order'),
    path('service-provider/order/<int:order_id>/complete/', views.complete_order, name='complete_order'),
    path('service-provider/verify-completion/<int:order_id>/', views.verify_completion_pin, name='verify_completion_pin'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('reverse-geocode/', views.reverse_geocode, name='reverse_geocode'),
]
