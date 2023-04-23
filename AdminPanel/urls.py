from django.urls import path,include
from .import views

urlpatterns = [
    path("adminlogin/", views.adminLogin,name = 'adminlogin'), 
    path("dashboard/", views.adminHome,name = 'dashboard'), 
    path("admin_profile/", views.admin_profile,name = 'admin_profile'), 
    path("user_management/", views.user_management,name = 'user_management'), 
    path("block/<int:id>", views.block,name = 'block'), 
    path("unblock/<int:id>", views.block,name = 'unblock'),     

    path("category_management/", views.category_management,name = 'category_management'), 
    path("add_category/", views.add_category,name = 'add_category'), 
    path("edit_category/<int:id>", views.edit_category,name = 'edit_category'), 
    path("delete_category/<int:id>", views.delete_category,name = 'delete_category'), 

    
    path("subcategory/", views.sub_category,name = 'subcategory'), 
    path("add_subcategory/", views.add_sub_cat,name = 'add_subcategory'), 
    path("edit_subcategory/<int:id>", views.edit_sub_cat,name = 'edit_subcategory'), 
    path("delete_subcategory/<int:id>", views.delete_sub_cat,name = 'delete_subcategory'), 
    # path('fetch_subcategories/', views.fetch_subcategories, name='fetch_subcategories'), 
    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),

    path("brand_manage/", views.brand_manage,name = 'brand_manage'), 
    path("add_brand/", views.add_brand,name = 'add_brand'), 
    path("edit_brand/<int:id>", views.edit_brand,name = 'edit_brand'), 
    path("delete_brand/<int:id>", views.delete_brand,name = 'delete_brand'), 

    
    path("product_management/", views.product_management,name = 'product_management'), 
    path("add_product/", views.add_product,name = 'add_product'),  
    path("edit_product/<int:id>", views.edit_product,name = 'edit_product'),
    path("delete_product/<int:id>", views.delete_product,name = 'delete_product'),

    path("order_management/", views.order_management,name ='order_management'),
    
    path("delivery_status/<int:id>/", views.delivery_status ,name='delivery_status'),
    # path("cancel_order/<int:id>/", views.cancel_order,name = 'cancel_order'),  
    path("sales/", views.sales,name = 'sales'),  

    path("adminlogout/", views.adminLogout,name = 'adminlogout'),  


    path("sales_excel_report/", views.sales_excel_report,name = 'sales_excel_report'),  
    path("sales_csv_report/", views.sales_csv_report,name = 'sales_csv_report'),  


    path("coupon/", views.coupon,name = 'coupon'),  
    path("add_coupon/", views.add_coupon,name = 'add_coupon'),  
    path("edit_coupon/<int:id>/", views.edit_coupon, name='edit_coupon'),
    path("delete_coupon/<int:id>/", views.delete_coupon, name='delete_coupon'),

    path("banner", views.banner, name='banner'),
    path("add_banner", views.add_banner, name='add_banner'),
    path("edit_banner/<int:id>",views.edit_banner,name='edit_banner'),
    path("delete_banner/<int:id>",views.delete_banner,name='delete_banner'),

    path('category_sales_report/', views.category_sales_report, name='category_sales_report'),


    
    
]