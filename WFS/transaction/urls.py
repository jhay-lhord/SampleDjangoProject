from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name="index"),
    path('product/',views.product, name = "product"),
    path('refill/',views.refill, name = "refill"),
    path('transaction/',views.transaction, name = "transaction"),
    path('water_tank/',views.water_tank, name = "water_tank"),
    path('sales/',views.sales, name = "sales"),
    path('customer_pdf/',views.customer_pdf, name = "customer_pdf"),
    path('employee_pdf/',views.employee_pdf, name = "employee_pdf"),
    path('water_tank_pdf/',views.water_tank_pdf, name = "water_tank_pdf"),
    path('refills_pdf/',views.refills_pdf, name = "refills_pdf"),

    path('delete_product/<int:pk>',views.delete_product, name = "delete_product"),
    path('delete_refill/<int:pk>',views.delete_refill, name = "delete_refill"),
    path('delete_transaction/<int:pk>',views.delete_transaction, name = "delete_transaction"),
    path('delete_water_tank/<str:pk>',views.delete_water_tank, name = "delete_water_tank"),

    path('update_product/<int:pk>',views.update_product, name = "update_product"),
    path('update_refill/<int:pk>',views.update_refill, name = "update_refill"),
    path('update_transaction/<int:pk>',views.update_transaction, name = "update_transaction"),
    path('update_water_tank/<str:pk>',views.update_water_tank, name = "update_water_tank"),

    


]
