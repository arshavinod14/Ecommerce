import os
import random
from dotenv import load_dotenv
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account,Address
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
from django.views.decorators.cache import cache_control
from django.core.exceptions import ObjectDoesNotExist

num1 = 0
phone = 0



@cache_control(no_cache=True, must_revalidate=True)
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
        
@cache_control(no_cache=True, must_revalidate=True)
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
                messages.error(request, 'Email Id or Password is wrong!')
                return redirect(loginacc)
    else:
        form = LoginForm()
        return render(request, 'user_login.html', {'form': form})


def otp(request):
    global phone

    if request.method=='POST':
        phone = request.POST['phone']
        if Account.objects.filter(phone=phone).exists():

            print(phone)
            # account_sid = 'ACe1027a6fa785c6a6c4a87e4926ab8c52'
            account_sid = os.getenv('ACCOUNT_SID')
            # auth_token = 'b49abeb8b8fa38c0a2a0542adfcc4523'
            auth_token = os.getenv('AUTH_TOKEN')
            service_sid = os.getenv('SERVICE_SID')
            print(account_sid,auth_token)
            client = Client(account_sid, auth_token)

            verification = client.verify \
                    .v2 \
                    .services(service_sid) \
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
        account_sid = os.getenv('ACCOUNT_SID')
        auth_token = os.getenv('AUTH_TOKEN')
        service_sid = os.getenv('SERVICE_SID')
        client = Client(account_sid, auth_token)
        try:
            verification_check = client.verify \
                            .v2 \
                            .services(service_sid) \
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
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return redirect('signup')


            try:
                Account.objects.get(email=email)
                messages.error(request, "User with this email already exists!")
                return redirect('signup')
            except ObjectDoesNotExist:
                pass

            try:
                Account.objects.get(phone=phone)
                messages.error(request, "User with this phone number already exists!")
                return redirect('signup')
            except ObjectDoesNotExist:
                pass

            
            user = Account.objects.create_user(name, email, phone, password)
            user.name = name
            user.email = email
            user.phone = phone
            user.save()

            messages.success(request, "Registered Successfully!")
            return redirect(loginacc)

    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})




def sign_out(request):
    if request.user.is_authenticated:
        logout(request)
        print("LoggedOut")
        # messages.success(request, 'Logged Out Successfully')
        return redirect(index)


def check(request):
    return render(request,'otp.html')

def address(request):
    print("11111111111")
    if request.user.is_authenticated:
        print("22222222222222")
        # ad = Address.objects.filter(user=request.user)
        print("33333333333")
        # context = {'ad':ad}
        if request.method == 'POST':
            name = request.POST['name']
            phone = request.POST['phone']
            email = request.POST['email']
            address1 = request.POST['address1']
            country = request.POST['country']
            state = request.POST['state']
            zip = request.POST['zip']
            add = Address(user=request.user, name=name, phone=phone, email=email, address1=address1,
                        country=country, state=state, zip=zip)
            add.save()
            # return redirect('check_out')
        return redirect('check_out')
    return redirect(index)








    