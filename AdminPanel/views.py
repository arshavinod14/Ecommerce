from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from store.models import Account
from product.models import Product,Category,SubCategory
from order.models import Order,OrderItem
from django.contrib.auth.models import User
from .forms import *
from product.forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.postgres.search import SearchVector
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

@never_cache
def adminLogin(request):
    if request.user.is_authenticated and request.user.is_staff and request.user.is_admin:
        return redirect(adminHome)
    # if request.user.is_authenticated:
    #     return redirect()
    if request.method=='POST':
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email,password=password)
            if user is not None:
                if not user.is_staff:
                    messages.error(request, "You are not authorized to access this webpage!!!")
                    return render(request, 'admin_login.html')
                login(request,user)
                #messages.success(request, 'Successfully logged in')
                return redirect(adminHome)
            else:
                messages.error(request, 'EmailId or Password is wrong!')
                return redirect(adminLogin)
    return render(request,'admin_login.html')



@never_cache
def adminHome(request):
    if request.user.is_authenticated and request.user.is_staff:
        print('Testing')
        order = Order.objects.all()
        product = Product.objects.all()
        customers = Account.objects.all()
    
        order = order.count()
        product = product.count()
        customers = customers.count()

        total_price = Order.objects.aggregate(Sum('total_price'))['total_price__sum']

        context = {
                'order_count':order,
                'total_price': total_price,
                'product_count':product,
                'customers_count': customers,  
                }
        
        return render(request, 'adminhome.html',context)
    return redirect(adminLogin)
    # if request.user.is_authenticated and request.user.is_staff:
    #     records = Account.objects.all()
    #     print(records)
    #     return render(request,'adminhome.html',{'records':records}) 
    # return redirect(adminHome)

def admin_profile(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            email = request.POST.get('email')
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Update email if it has changed
            if email and email != user.email:
                user.email = email
                user.save()
                messages.success(request, 'Email updated successfully')

            if current_password and new_password and confirm_password:

                if user.check_password(current_password):
        
                    if new_password == confirm_password:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, 'Password updated successfully')
                    else:
                        messages.error(request, 'New password and confirm password do not match')
                else:
                    messages.error(request, 'Current password is incorrect')
        return render(request, 'admin_profile.html', {'user': user})

    return redirect('adminlogin')







@never_cache
def user_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        records = Account.objects.all().order_by('id')
        print(records)
        if request.method == 'GET'and request.GET.get('search') is not None:
            print(request.GET)
            records = Account.objects.annotate(search=SearchVector('name','email')).filter(search=request.GET.get('search'))
            return render(request, 'user_management.html',{'records':records})

        return render(request, 'user_management.html',{'records':records})
    return redirect(adminLogin)

def block(request,id):
    if request.user.is_authenticated and request.user.is_active and request.user.is_staff:
        flag = Account.objects.all().values('is_active').get(id=id)
        if flag['is_active'] == True:
            Account.objects.filter(id=id).update(is_active=False)
            return redirect(user_management)
        else:
            Account.objects.filter(id=id).update(is_active=True)
            return redirect(user_management)
    return redirect(user_management)
        

from django.core.paginator import Paginator

def product_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        products = Product.objects.all().order_by('id')
        print(products)
        if request.method == 'GET' and request.GET.get('search') is not None:
            print(request.GET)
            search_query = request.GET.get('search')
            products = Product.objects.annotate(search=SearchVector('name')).filter(search=search_query)
            paginator = Paginator(products, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'products': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'product_management.html', context)

        paginator = Paginator(products, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'products': page_obj, 'paginator': paginator}
        return render(request, 'product_management.html', context)
    return redirect(adminLogin)


    
@never_cache
def add_product(request):
    if request.user.is_authenticated and request.user.is_staff:
        form = ProductForm()
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            print("->>>>",request.POST)
            print("->>>>",request.FILES)
            
            if form.is_valid():
                form.save()
            return redirect(product_management)
            
        else:
            categories = Category.objects.all()
            subcategories = SubCategory.objects.all()
            # size = Size.objects.all()
            # print("Form error:",form.errors)
            return render(request, 'add_product.html', {'form': form, 'categories': categories, 'subcategories': subcategories})
            
    return redirect(product_management)





def edit_product(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        product = Product.objects.get(id=id)
        path = request.path
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                return redirect(product_management)
        else:
            product = Product.objects.get(id=id)
            form = ProductForm(instance=product)
            return render(request, 'edit_product.html', context={'form': form,'path': path})
    return redirect(product_management)

def delete_product(request,id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id)
        product.delete()
        #messages.success(request, "Deleted a record successfully.")
        return redirect(product_management)
    return redirect(product_management)

# def fetch_subcategories(request):
#     category_id = request.GET.get('category_id')
#     subcategories = SubCategory.objects.filter(category_id=category_id)
#     return JsonResponse({'subcategories': [{'id': s.id, 'name': s.name} for s in subcategories]})


def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id)
    data = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]
    return JsonResponse(data, safe=False)



def category_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        category= Category.objects.all().order_by('id')
        print(category)
        if request.method == 'GET'and request.GET.get('search') is not None:
            print(request.GET)
            category= Category.objects.annotate(search=SearchVector('name')).filter(search=request.GET.get('search'))
            return render(request, 'category_management.html',{'category':category})

        return render(request, 'category_management.html',{'category':category})
    return redirect(category_management)

def add_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            name = request.POST['name']
            offer = request.POST['offer']
            slug = request.POST['slug']
            category = Category(name=name, offer=offer,slug=slug)
            category.save()
            return redirect(category_management)
    return render(request, 'add_category.html')

def edit_category(request,id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST['name']
            offer = request.POST['offer']
            Category.objects.filter(id=id).update(name=name,offer=offer)
        else:
            data = Category.objects.get(id=id)
            return render(request, 'edit_category.html',{'category':data})
    #messages.success(request, "Details have been Updated")
    return redirect(category_management)

def delete_category(request,id):
    if request.user.is_authenticated:
        category = Category.objects.get(id=id)
        category.delete()
        #messages.success(request, "Deleted a record successfully.")
        return redirect(category_management)
    return redirect(adminHome)

def sub_category(request):
    if request.user.is_authenticated and request.user.is_staff:
            subcategory= SubCategory.objects.all().order_by('id')
            print(subcategory)
            if request.method == 'GET'and request.GET.get('search') is not None:
                print(request.GET)
                subcategory= SubCategory.objects.annotate(search=SearchVector('name')).filter(search=request.GET.get('search'))
                return render(request, 'subcategory_manage.html',{'subcategory':subcategory})

            return render(request, 'subcategory_manage.html',{'subcategory':subcategory})
    return redirect(adminHome)


def add_sub_cat(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            name = request.POST['name']
            slug = request.POST['slug']
            category_id = request.POST['category']
            category = Category.objects.get(id=category_id)
            subcategory=SubCategory(name=name,slug=slug,category=category)
            subcategory.save()
            return redirect(sub_category)
        categories = Category.objects.all()
        return render(request, 'add_subcategory.html',{'categories': categories})
    return redirect(sub_category)

def edit_sub_cat(request,id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST['name']
            SubCategory.objects.filter(id=id).update(name=name)
        else:
            data = SubCategory.objects.get(id=id)
            return render(request, 'edit_subcategory.html',{'subcategory':data})
    #messages.success(request, "Details have been Updated")
    return redirect(sub_category)

def delete_sub_cat(request,id):
    if request.user.is_authenticated:
        subcategory = SubCategory.objects.get(id=id)
        subcategory.delete()
        #messages.success(request, "Deleted a record successfully.")
        return redirect(sub_category)
    return redirect(adminHome)


def brand_manage(request):
    if request.user.is_authenticated and request.user.is_staff:
        brand = Brand.objects.all().order_by('id')
        if request.method == 'GET' and request.GET.get('search') is not None:
            brand = Brand.objects.annotate(search=SearchVector('name')).filter(search=request.GET.get('search'))
            return render(request, 'brand_manage.html',{'brand':brand})
        return render(request, 'brand_manage.html',{'brand':brand})
    return redirect(brand_manage)

def add_brand(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            name = request.POST['name']
            brand = Brand(name=name)
            brand.save()
            return redirect(brand_manage)
    return render(request, 'add_brand.html')

def edit_brand(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST['name']
            Brand.objects.filter(id=id).update(name=name)
        else:
            data = Brand.objects.get(id=id)
            return render(request, 'edit_brand.html',{'brand':data})
    #messages.success(request, "Details have been Updated")
    return redirect(brand_manage)

def delete_brand(request, id):
    if request.user.is_authenticated:
        brand = Brand.objects.get(id=id)
        brand.delete()
        #messages.success(request, "Deleted a record successfully.")
        return redirect(brand_manage)
    return redirect(adminHome)




@never_cache
def adminLogout(request):
    if request.user.is_authenticated and request.user.is_staff:
        logout(request)
        print("LoggedOut")
        messages.success(request, 'Logged Out Successfully')
        return redirect(adminLogin)
    return render(request,'admin_login.html')



def order_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        order = Order.objects.all()
        order_items = OrderItem.objects.all()
        print("orderitems-------->",order_items)
        print(order)
        # if request.method == 'GET'and request.GET.get('search') is not None:
        #     print(request.GET)
        #     order = Order.objects.annotate(search=SearchVector('user.name')).filter(search=request.GET.get('search'))
        #     return render(request, 'order_management.html',{'order':order})

        return render(request, 'order_management.html',{'order':order})
        
    return redirect(adminLogin)


def delivery_status(request, id):
    print("eeeeeeee")
    order = Order.objects.get(id=id)
    if order.delivery_status == 'Pending':
        order.delivery_status = 'Shipped'
    elif order.delivery_status == 'Shipped':
        order.delivery_status = 'Out for delivery'
    elif order.delivery_status == 'Out for delivery':
        order.delivery_status = 'Delivered'
    order.save()
    return redirect(order_management)


def cancel_order(request, id):
    order = Order.objects.get(id=id)
    if order.delivery_status == 'Delivered':
        return HttpResponse('This order has already been delivered and cannot be canceled.')
    order.status = False
    order.delivery_status = 'Cancelled'
    order.save()
    return redirect(order_management)









