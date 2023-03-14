from django.urls import path
from .import views

urlpatterns = [
    path("", views.index,name = 'home'), 
    path("login/",views.loginacc,name='login'),
    path("signup/",views.signup,name='signup'),
    path("logout/",views.sign_out,name='logout'),
    path("otp/",views.otp,name='otp'),
    path("otp_verify/",views.otp_verify,name='otp_verify'),
    
    path("check/",views.check,name='check'),
    
]