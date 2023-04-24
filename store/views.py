import json
import os
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from AdminPanel.models import Banner
from .models import Account,Address
from product.models import Brand, CartItems, Category,Product, SubCategory,Wishlist,GuestCart
from .forms import *
from AdminPanel.views import adminHome
from twilio.rest import Client,TwilioException
from django.views.decorators.cache import cache_control
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.search import SearchVector
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

num1 = 0
phone = 0

@cache_control(no_cache=True, must_revalidate=True)
def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(adminHome)
        else:
            banner = Banner.objects.all()
            products = Product.objects.all()
            category = request.GET.get('category', None)
            subcategory = request.GET.get('subcategory', None)
            if category:
                products_list = Product.objects.filter(category=request.GET.get('category'))

            if subcategory:
                products_list = Product.objects.filter(subcategory=request.GET.get('subcategory'))

            category = Category.objects.all()
            s = []
            for i in category:
                s.append({
                    'id': i.id,
                    'name': i.name,
                    'subcategories': SubCategory.objects.filter(category=i).values()
                })
            
            context = {
                'category': s,
                'banner': banner,
                'products': products
            }
            
            return render(request, 'index.html', context)
    else:
        banner = Banner.objects.all()
        products = Product.objects.all() 
        context = {'banner': banner, 'products': products}
        return render(request, 'index.html', context)

        
@cache_control(no_cache=True, must_revalidate=True)
def loginacc(request):
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
                
                if not request.session.session_key:
                    request.session.create()
                request.session['guest_key']=request.session.session_key
                sessionId = request.session['guest_key']
                login(request, user)
                guest_item = GuestCart.objects.filter(user_ref=sessionId).values()
                for i in guest_item:
                    print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii:",i)
                    i.pop('user_ref')
                    i['user'] = request.user
                    CartItems.objects.create(**i)
                guest_item = GuestCart.objects.filter(user_ref=sessionId)
                guest_item.delete()
                print("logged!!")
                messages.success(request, 'Successfully logged in')
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
            account_sid = os.getenv('ACCOUNT_SID')
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

            # Check if email is valid
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Please enter a valid email address!")
                return redirect('signup')

            try:
                Account.objects.get(email=email)
                messages.error(request, "User with this email already exists!")
                return redirect('signup')
            except ObjectDoesNotExist:
                pass

            # Check if phone number is valid
            if not phone.isdigit() or len(phone) != 10:
                messages.error(request, "Please enter a valid 10 digit phone number!")
                return redirect('signup')

            try:
                Account.objects.get(phone=phone)
                messages.error(request, "User with this phone number already exists!")
                return redirect('signup')
            except ObjectDoesNotExist:
                pass

            # Check if password is strong
            if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
                messages.error(request, "Password should be at least 8 characters long and should contain at least one letter and one number!")
                return redirect('signup')
            
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


def profile(request):
    if request.user.is_authenticated:
        addresses = Address.objects.filter(user=request.user)
        user = request.user
        if request.method == 'POST':
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                request.user.profile_picture = profile_picture
                messages.success(request, 'Profile Picture has been updated!')
                request.user.save()

            name = request.POST.get('name')
            email = request.POST.get('email')
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Update user profile information
            if (user.name != name) or (user.email != email):
                user.name = name
                user.email = email
                user.save()
                messages.success(request, 'Profile updated successfully')
            # Update user password
            if current_password and new_password and confirm_password:
                if user.check_password(current_password):
                    if new_password == confirm_password:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'Password updated successfully')
                        print(messages)
                    else:
                        messages.error(request, 'New password and confirm password do not match')
                        print(messages)
                else:
                    messages.error(request, 'Current password is incorrect')
                    print(messages)
            
            return redirect('profile')
        return render(request, 'profile.html')
    messages.error(request,'login to view the profile')
    return redirect(loginacc)


def get_address(request):
    print('got to address function')
    if request.user.is_authenticated:
        addresses = Address.objects.filter(user=request.user)
        usersAddress = list(addresses.values())
        json_data = json.dumps(usersAddress)
        return JsonResponse(json_data,safe=False)


def edit_address(request, id):
    print("this is edit address function")
    if request.user.is_authenticated:
        address = Address.objects.get(id=id)
        return JsonResponse({
            "name": address.name,
            "address1": address.address1,
            "phone":address.phone,
            "state": address.state,
            "zip":address.zip,
            "country": address.country,
            "email": address.email,
            "id":id
        })

def update_address(request):
    print('ddddddddddddddddddddddddd')
    if request.method == "POST":
        id = request.POST.get('id')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address1 = request.POST.get('address1')
        state = request.POST.get('state')
        country = request.POST.get('country')
        zip = request.POST.get('zip')

        print(id,name,phone,address1,state,country,zip)
        address = Address.objects.get(id=id)
        print(address)

        address.name = name
        address.phone = phone
        address.address1 = address1
        address.state = state
        address.country = country
        address.zip = zip
        address.save()
        messages.success(request, 'Address updated successfully')
        return JsonResponse({'success':True})


def delete_address(request,id):
    print("this is delete function")
    if request.user.is_authenticated:
        address = Address.objects.get(id=id)
        address.delete()
        return JsonResponse({'message': 'Address deleted successfully'})




def add_to_wishlist(request, id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=request.POST.get('id'))
        wishlist_item = Wishlist.objects.filter(product=product, user=request.user)
        if wishlist_item.exists():
            return JsonResponse({'message': 'This product is already in your wishlist.'})
        else:
            wishlist_item = Wishlist.objects.create(product=product, user=request.user)
            # messages.success(request, "Product added to your wishlist.")
        # remove messages from session after displaying them
        messages.get_messages(request)
        # Return a JSON response
        return JsonResponse({'message': 'Product added to your wishlist.'})
    else:
        # Return an error response
        return JsonResponse({'error': 'Please log in to add products to your wishlist.'})



def wishlist(request):
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)
        print(wishlist_items)

        context = {
            'wishlist_items':wishlist_items,

        }
        return render(request, 'wishlist.html',context)
    else:
        messages.error(request, "Please log in to view your wishlist.")

        return redirect('login')


def remove_wishlist(request, id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id)
        wishlist_item = Wishlist.objects.filter(product=product, user=request.user)
        if wishlist_item.exists():
            wishlist_item.delete()
            messages.success(request, "Product removed from your wishlist.")
        else:
            messages.info(request, "This product is not in your wishlist.")
        return redirect('wishlist')
    else:
        messages.error(request, "Please log in to remove products from your wishlist.")
        return redirect('login')

def search(request):
    search_query = request.GET.get('search')
    if search_query:
        search_vector = SearchVector('name', 'category__name', 'subcategory__name')
        search_query = SearchQuery(search_query, config='english')
        products = Product.objects.annotate(
            search=search_vector, 
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')
        count_p = products.count()
        brand = Brand.objects.all()
        category = Category.objects.all()
        return render(request, 'products.html', {'products': products,'count_p':count_p,'brand':brand,'category':category})

def handler404(request, exception):
    return render(request, '404.html', status=404)


def blog(request):
    return render(request,'blog.html')

def contact(request):
    return render(request,'contact.html')