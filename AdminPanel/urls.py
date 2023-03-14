from django.urls import path,include
from .import views

urlpatterns = [
    path("adminlogin/", views.adminLogin,name = 'adminlogin'), 
    path("dashboard/", views.adminHome,name = 'dashboard'), 
    path("user_management/", views.user_management,name = 'user_management'), 
    path("block/<int:id>", views.block,name = 'block'), 
    path("unblock/<int:id>", views.block,name = 'unblock'),     

    path("category_management/", views.category_management,name = 'category_management'), 
    path("add_category/", views.add_category,name = 'add_category'), 
    path("edit_category/<int:id>", views.edit_category,name = 'edit_category'), 
    path("delete_category/<int:id>'", views.delete_category,name = 'delete_category'), 

    
    path("subcategory/'", views.sub_category,name = 'subcategory'), 
    path("add_subcategory/'", views.add_sub_cat,name = 'add_subcategory'), 
    path("edit_subcategory/<int:id>", views.edit_sub_cat,name = 'edit_subcategory'), 
    path("delete_subcategory/<int:id>'", views.delete_sub_cat,name = 'delete_subcategory'), 
    path('fetch_subcategories/', views.fetch_subcategories, name='fetch_subcategories'),

    
    path("product_management/", views.product_management,name = 'product_management'), 
    path("add_product/", views.add_product,name = 'add_product'),  
    path("edit_product/<int:id>", views.edit_product,name = 'edit_product'),
    path("delete_product/<int:id>", views.delete_product,name = 'delete_product'),
    
    path("adminlogout/", views.adminLogout,name = 'adminlogout'),   
]