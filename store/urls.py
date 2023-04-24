from django.urls import path
from .import views

handler404 = 'store.views.handler404'
urlpatterns = [
    path("", views.index,name = 'home'), 
    path("login/",views.loginacc,name='login'),
    path("signup/",views.signup,name='signup'),
    path("logout/",views.sign_out,name='logout'),
    path("otp/",views.otp,name='otp'),
    path("otp_verify/",views.otp_verify,name='otp_verify'),
    
    path("address/",views.address,name='address'),

    path('profile/',views.profile,name='profile'),
    path('get_address/',views.get_address,name='get_address'),
    path('edit_address/<int:id>',views.edit_address,name='edit_address'),
    path('delete_address/<int:id>',views.delete_address,name='delete_address'),
    path('update_address',views.update_address,name='update_address'),
    
    
    path('add_to_wishlist/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('remove_wishlist/<int:id>/',views.remove_wishlist,name='remove_wishlist'),
    path('search/',views.search,name='search'),

    path('blog/',views.blog,name='blog'),
    path('contact/',views.contact,name='contact'),

    




    # path('single_wishlist/<int:id>/', views.single_wishlist, name='single_wishlist'),
    # path('update_address/<int:id>/',views.update_address,name='update_address'),



    
    

    
    
    
]