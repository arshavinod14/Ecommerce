import random
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account
import product.views
from product.models import Product,Category,SubCategory,CartItems
from .forms import *
from django.contrib.auth.hashers import check_password
from django.forms import ValidationError
from django.contrib.auth.decorators import login_required
from AdminPanel.views import adminHome
from django.conf import settings
from twilio.rest import Client
from twilio.rest import TwilioException

num1 = 0
phone = 0

def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(adminHome)
        else:
            cart_items = CartItems.objects.filter(user=request.user)
            count = cart_items.count()
            return render(request,'index.html',{'count':count})
    else:
        return render(request,'index.html')
        

def loginacc(request):
    # if request.user.is_authenticated and request.user.is_staff :
    #     #print(request.user)
    #     return redirect(adminHome)

    if request.user.is_authenticated:
        print(request.user)
        return redirect(index)

    if request.method == 'POST':
        # print("erger")
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            print(user)
            if user is not None:
                    # Log the user in 
                if user.is_staff:
                    messages.error(request, "You are not authorized to access this webpage!!!")
                    return render(request, 'user_login.html',{'form': form})
                login(request, user)
                print("logged!!")
                # messages.success(request, 'Successfully logged in')
                return redirect(index)
            else:
                messages.error(request, 'EmailId or Password is wrong!')
    else:
        form = LoginForm()
        return render(request, 'user_login.html', {'form': form})


def otp(request):
    global phone

    if request.method=='POST':
        phone = request.POST['phone']
        if Account.objects.filter(phone=phone).exists():

            print(phone)
            account_sid = 'ACe1027a6fa785c6a6c4a87e4926ab8c52'
            auth_token = '19b2ed95456879612442809ae30f2d82'
            client = Client(account_sid, auth_token)

            verification = client.verify \
                    .v2 \
                    .services('VA5cd8387315be948efb3ddd9158276d6a') \
                    .verifications \
                    .create(to='[+91]'+str(phone), channel='sms')

            print(verification)
            if Account.objects.filter(phone=phone).exists():
                    return redirect(otp_verify)
        else:
            messages.error(request, "You are not a registered user!")
            return redirect(loginacc)

    return render(request,'otp_login.html')

def otp_verify(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        print(otp)
        account_sid = 'ACe1027a6fa785c6a6c4a87e4926ab8c52'
        auth_token = '19b2ed95456879612442809ae30f2d82'
        client = Client(account_sid, auth_token)
        try:
            verification_check = client.verify \
                            .v2 \
                            .services('VA5cd8387315be948efb3ddd9158276d6a') \
                            .verification_checks \
                            .create(to='[+91]'+str(phone), code=otp)

            if verification_check.status == 'approved':
                user = Account.objects.get(phone=phone)
                login(request,user)
                return redirect(index)
            else:
                messages.error(request, ("Wrong OTP"))
        except TwilioException as e:
            messages.error(request, ("Wrong OTP"))
    return render(request, 'otp.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data['name']
            email=form.cleaned_data['email']
            phone=form.cleaned_data['phone']
            password=form.cleaned_data['password']
            confirm_password=form.cleaned_data['confirm_password']
            if password!=confirm_password:
                messages.error(request,"passwords do not match!!")
                return redirect('signup')

            user = Account.objects.create_user(name,email,phone,password)
            user.name = name
            user.email = email
            user.phone = phone
            user.save()

            #login(request,user)
            messages.success(request,"Registered Successfully!")
            return redirect(loginacc)
            
    else:
            form = SignUpForm()
    return render(request,'signup.html',{'form':form})



def sign_out(request):
    if request.user.is_authenticated:
        logout(request)
        print("LoggedOut")
        # messages.success(request, 'Logged Out Successfully')
        return redirect(index)


def check(request):
    return render(request,'otp.html')

    