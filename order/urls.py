from django.urls import path
from .import views

urlpatterns = [
    path("place_order/",views.place_order,name='place_order'),
    path("order_detail/",views.order_detail, name='order_detail'),
    path('order_cancel/<int:id>/', views.order_cancel, name='order_cancel'),
    path('checking_confirm/',views.checking_confirm,name='checking_confirm'),
    path('invoice/<int:id>', views.invoice, name='invoice'),
    # path('delete/', views.delete, name='delete'),
    path('success/', views.success, name='success'),
    path('get_add/', views.get_add, name='get_add'),
    path('order_return/<int:id>', views.order_return, name='order_return'),
  
    

]