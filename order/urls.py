from django.urls import path
from .import views

urlpatterns = [
    path("place_order/",views.place_order,name='place_order'),
    path("order_detail/",views.order_detail, name='order_detail'),
    path('order_cancel/<int:id>/', views.order_cancel, name='order_cancel'),
    path('checking_confirm/',views.checking_confirm,name='checking_confirm'),
    path('invoice/<int:id>', views.invoice, name='invoice'),
    # path('delete/', views.delete, name='delete'),

    
    

]