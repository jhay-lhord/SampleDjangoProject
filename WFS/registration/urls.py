from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserLoginView.as_view(), name = "user_login"),
    path('register/',views.user_register, name = "user_register"),
    path('logout/',views.UserLogoutView.as_view(), name = "user_logout"),
    path('employee/',views.employee, name = "employee"),
    path('customer/',views.customer, name = "customer"),

    path('update_customer/<int:pk>',views.update_customer, name = "update_customer"),
    path('update_employee/<int:pk>',views.update_employee, name = "update_employee"),

    path('delete_employee/<int:pk>/',views.delete_employee, name = "delete_employee"),
    path('delete_customer/<int:pk>/',views.delete_customer, name = "delete_customer"),

]