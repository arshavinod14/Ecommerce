from django.urls import path
from .import views

urlpatterns = [

    path("product_view/",views.product_view,name='product_view'),
    path("product_detail/<int:id>/",views.single_product,name='product_detail'),

    path("cart/<int:id>/",views.add_to_cart,name='cart'),
    path("view_cart/",views.view_cart,name='view_cart'),
    path("delete_cart/<int:id>/",views.remove_cart,name='delete_cart'),

    path("update_quantity/",views.update_quantity,name='update_quantity'),
    path('check_stock/', views.check_stock, name='check_stock'),
    path('check_out/', views.check_out, name='check_out'),

    path('women_product/', views.women_product, name='women_product'),
    path('men_product/', views.men_product, name='men_product'),
    path('category/<slug:category_slug>/<slug:subcategory_slug>/', views.category_products, name='category_products'),

    path('sort_products/', views.sort_products, name='sort_products'),

]

    
    


