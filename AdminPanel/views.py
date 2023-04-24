import json
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.urls import reverse
from AdminPanel.models import Banner
from store.models import Account
from product.models import Coupon, Product,Category,SubCategory
from order.models import Order,OrderItem
from .forms import *
from product.forms import *
from django.http import HttpResponse
from django.contrib.postgres.search import SearchVector
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.db.models import Sum
from django.core.paginator import Paginator
from django.db.models import Sum
from datetime import datetime


# Create your views here.

@never_cache
def adminLogin(request):
    if request.user.is_authenticated and request.user.is_staff and request.user.is_admin:
        return redirect(adminHome)
    if request.method=='POST':
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email,password=password)
            if user is not None:
                if not user.is_staff:
                    messages.error(request, "You are not authorized to access this webpage!!!")
                    return render(request, 'admin_login.html')
                login(request,user)
                return redirect(adminHome)
            else:
                messages.error(request, 'EmailId or Password is wrong!')
                return redirect(adminLogin)
    return render(request,'admin_login.html')



@never_cache
def adminHome(request):
    if request.user.is_authenticated and request.user.is_staff:
        order = Order.objects.all()
        products = Product.objects.all()
        customers = Account.objects.all()
        order = order.count()
        product = products.count()
        customers = customers.count()


        total_price = Order.objects.filter(delivery_status='Delivered').aggregate(Sum('total_price'))['total_price__sum']
        a =[]
        for i in products:
            z = OrderItem.objects.filter(product_id=i.id).values('order')
            o = Order.objects.filter(id__in=z,delivery_status='Delivered').aggregate(Sum('total_price'))


            if o['total_price__sum'] is None or o is None:
                a.append({'title':i.name,'price':0})
            else:
                a.append({'title':i.name,'price':o['total_price__sum']})
        context = {
                'order_count':order,
                'total_price': total_price,
                'product_count':product,
                'customers_count': customers,  
                'a':a,
                }
        
        return render(request, 'adminhome.html',context)
    return redirect(adminLogin)


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
        if request.method == 'GET'and request.GET.get('search') is not None:
            search_query = request.GET.get('search')
            records = Account.objects.annotate(search=SearchVector('name','email')).filter(search=request.GET.get('search'))
            paginator = Paginator(records, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'records': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'user_management.html',context)

        paginator = Paginator(records, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'records': page_obj, 'paginator': paginator}
        return render(request, 'user_management.html',context)
    return redirect(adminLogin)


def block(request,id):
    if request.user.is_authenticated and request.user.is_active and request.user.is_staff:
        flag = Account.objects.all().values('is_active').get(id=id)
        if flag['is_active'] == True:
            Account.objects.filter(id=id).update(is_active=False)
            messages.success(request, "Blocked.")
            return redirect(user_management)
        else:
            Account.objects.filter(id=id).update(is_active=True)
            messages.success(request, "Unblocked.")
            return redirect(user_management)
    return redirect(user_management)
        



def product_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        products = Product.objects.all().order_by('id')
        if request.method == 'GET' and request.GET.get('search') is not None:
            search_query = request.GET.get('search')
            products = Product.objects.annotate(search=SearchVector('name')).filter(search=search_query)
            paginator = Paginator(products, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'products': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'product_management.html', context)

        paginator = Paginator(products, 5)
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
            
            if form.is_valid():
                form.save()
            messages.success(request,'Product added successfully')
            return redirect(product_management)
            
        else:
            categories = Category.objects.all()
            subcategories = SubCategory.objects.all()
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
                messages.success(request,'Product edited successfully')
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
        messages.success(request, "Deleted a product successfully.")
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
        if request.method == 'GET'and request.GET.get('search') is not None:
            category= Category.objects.annotate(search=SearchVector('name')).filter(search=request.GET.get('search'))
            return render(request, 'category_management.html',{'category':category})

        return render(request, 'category_management.html',{'category':category})
    return redirect(category_management)


def add_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            name = request.POST['name']
            offer = request.POST['offer']
            try:
                if Category.objects.filter(name__iexact=name).exists():
                    messages.error(request, "Category already exists")
                else:
                    category = Category(name=name, offer=float(offer))
                    category.save()
                    messages.success(request, "Category Added")
                return redirect(category_management)
            except ValueError:
                messages.error(request, "Invalid input for 'offer'. Please enter a number.")
                return render(request, 'add_category.html')
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
    messages.success(request, "Category Updated")
    return redirect(category_management)

def delete_category(request,id):
    if request.user.is_authenticated:
        category = Category.objects.get(id=id)
        category.delete()
        messages.success(request, "Deleted a category successfully.")
        return redirect(category_management)
    return redirect(adminHome)

def sub_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        subcategory= SubCategory.objects.all().order_by('id')
        if request.method == 'GET' and request.GET.get('search') is not None:
            search_query = request.GET.get('search')
            subcategory = Product.objects.annotate(search=SearchVector('name')).filter(search=search_query)
            paginator = Paginator(subcategory, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'subcategory': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'subcategory_manage.html', context)

        paginator = Paginator(subcategory, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'subcategory': page_obj, 'paginator': paginator}
        return render(request, 'subcategory_manage.html', context)
    return redirect(adminHome)



def add_sub_cat(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            name = request.POST['name']
            category_id = request.POST['category']
            category = Category.objects.get(id=category_id)

            if SubCategory.objects.filter(name__iexact=name, category=category).exists():
                messages.error(request, "Subcategory already exists in the selected category")
            else:
                subcategory=SubCategory(name=name,category=category)
                subcategory.save()
                messages.success(request, "SubCategory Added")
            return redirect(sub_category)
        
        categories = Category.objects.all()
        return render(request, 'add_subcategory.html',{'categories': categories})
    
    return redirect(sub_category)


def edit_sub_cat(request, id):
    if request.user.is_authenticated:
        subcategory = SubCategory.objects.get(id=id)

        if request.method == 'POST':
            name = request.POST['name']
            category = subcategory.category

            if SubCategory.objects.filter(category=category, name__iexact=name).exclude(id=id).exists():
                messages.error(request, "Subcategory with this name already exists in this category!")
                return redirect('edit_subcategory', id=id)

            subcategory.name = name
            subcategory.save()

            messages.success(request, "Subcategory updated successfully!")
            return redirect(sub_category)

        return render(request, 'edit_subcategory.html', {'subcategory': subcategory})
    return redirect(sub_category)




def delete_sub_cat(request,id):
    if request.user.is_authenticated:
        subcategory = SubCategory.objects.get(id=id)
        subcategory.delete()
        messages.success(request, "Deleted subcategory successfully.")
        return redirect(sub_category)
    return redirect(adminHome)


def brand_manage(request):
    if request.user.is_authenticated and request.user.is_staff:
        brand = Brand.objects.all().order_by('id')
        if request.method == 'GET' and request.GET.get('search') is not None:
            search_query = request.GET.get('search')
            brand = Brand.objects.annotate(search=SearchVector('name')).filter(search=search_query)
            paginator = Paginator(brand, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'brand': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'brand_manage.html', context)

        paginator = Paginator(brand, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'brand': page_obj, 'paginator': paginator}
        return render(request, 'brand_manage.html', context)
    return redirect(adminHome)



from django.db.models import Q

def add_brand(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            name = request.POST['name']
            if Brand.objects.filter(Q(name__iexact=name)).exists():
                messages.error(request, 'A brand with this name already exists')
            else:
                brand = Brand(name=name)
                brand.save()
                messages.success(request,'Brand added successfully')
            return redirect(brand_manage)
    return render(request, 'add_brand.html')


def edit_brand(request, id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST['name']
            # Check if a brand with the same name already exists for a different ID
            existing_brand = Brand.objects.filter(name__iexact=name).exclude(id=id).first()
            if existing_brand:
                messages.error(request, "Brand with this name already exists!")
            else:
                Brand.objects.filter(id=id).update(name=name)
                messages.success(request, "Brand Updated")
            return redirect(brand_manage)
        else:
            data = Brand.objects.get(id=id)
            return render(request, 'edit_brand.html',{'brand':data})
    return redirect(brand_manage)


def delete_brand(request, id):
    if request.user.is_authenticated:
        brand = Brand.objects.get(id=id)
        product_count = brand.product_set.count() 
        if product_count > 0:
            messages.error(request, f"Cannot delete brand {brand.name} because it has {product_count} products.")
        else:
            brand.delete()
            messages.success(request, f"Deleted brand {brand.name} successfully.")
        return redirect(brand_manage)
    return redirect(adminHome)


@never_cache
def adminLogout(request):
    if request.user.is_authenticated and request.user.is_staff:
        logout(request)
        messages.success(request, 'Logged Out Successfully')
        return redirect(adminLogin)
    return render(request,'admin_login.html')



def order_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        # order = Order.objects.all().order_by('id')
        order = Order.objects.all().order_by('-order_at')  
        order_items = OrderItem.objects.all()
        if request.method == 'GET' and request.GET.get('search') is not None:
            search_query = request.GET.get('search')
            # order = Order.objects.annotate(search=SearchVector('name')).filter(search=search_query)
            order = Order.objects.annotate(search=SearchVector('items__product__name', 'order_id','payment_method', 'delivery_status')).filter(search=search_query).distinct()
            paginator = Paginator(order, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'order': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'order_management.html',context)
    
        paginator = Paginator(order, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'order': page_obj, 'paginator': paginator}
        return render(request, 'order_management.html', context)
    return redirect(adminLogin)



def delivery_status(request, id):
    order = Order.objects.get(id=id)
    if order.delivery_status == 'Pending':
        order.delivery_status = 'Shipped'
    elif order.delivery_status == 'Shipped':
        order.delivery_status = 'Out for delivery'
    elif order.delivery_status == 'Out for delivery':
        order.delivery_status = 'Delivered'
    order.save()
    page_number = request.GET.get('page', 1)
    url = reverse('order_management') + '?page=' + str(page_number)
    return redirect(url)



from django.core.paginator import Paginator

def sales(request):
    if request.user.is_authenticated and request.user.is_staff:
        today = datetime.now()
        #orders = Order.objects.filter(order_at__year=today.year, order_at__month=today.month)
        orders = Order.objects.filter(delivery_status='Delivered',order_at__year=today.year, order_at__month=today.month).order_by('-order_at')


        total_sales = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        #total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

        paginator = Paginator(orders, 10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'orders': page_obj,
            'total_sales': total_sales,
            'paginator': paginator,
            'page_obj': page_obj,
        }
        return render(request, 'sales_report.html', context)
    return redirect(adminLogin)


import csv
import xlwt
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa



def sales_excel_report(request):
    orders = Order.objects.all()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sales Report')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Order ID', 'User', 'Items', 'Total Price', 'Payment Method', 'Order At']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    for order in orders:
        row_num += 1
        row = [
            order.id,
            order.user.name,
            ', '.join([f'{item.product.name} ({item.quantity})' for item in order.items.all()]),
            order.total_price,
            order.payment_method,
            order.delivery_status,
            order.order_at.strftime('%d-%m-%Y %H:%M:%S')
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response

def sales_csv_report(request):
    orders = Order.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'User', 'Items', 'Total Price', 'Payment Method', 'Order At'])
    for order in orders:
        writer.writerow([
            order.id,
            order.user.name,
            ', '.join([f'{item.product.name} ({item.quantity})' for item in order.items.all()]),
            order.total_price,
            order.payment_method,
            order.delivery_status,
            order.order_at.strftime('%d-%m-%Y %H:%M:%S')
        ])
    return response


def coupon(request):
    if request.user.is_authenticated:
        coupon = Coupon.objects.all().order_by('id')
        return render(request,'coupon.html',{'coupon':coupon})


def add_coupon(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            code = request.POST['code']
            discount = request.POST['discount']
            valid_to = request.POST['valid_to']
            min_purchase_amount = request.POST['min_purchase_amount']
            coupon = Coupon(code = code,discount = discount,valid_to = valid_to,min_purchase_amount = min_purchase_amount)
            coupon.save()
            messages.success(request, "Coupon added successfully")
            return redirect('coupon')
    return render(request,'add_coupon.html')


def edit_coupon(request,id):
    if request.user.is_authenticated:
        coupon1 = Coupon.objects.get(id=id)
        if request.method == 'POST':
            code = request.POST['code']
            discount = request.POST['discount']
            valid = request.POST['valid_to']
            valid_date = datetime.strptime(valid, '%B %d, %Y').strftime('%Y-%m-%d')
            min = request.POST['min_purchase_amount']

            coupon1.code = code
            coupon1.discount= discount
            coupon1.valid_to = valid_date
            coupon1.min_purchase_amount = min

            coupon1.save()
            messages.success(request, "Coupon Updated")
            return redirect(coupon)

        return render(request,'edit_coupon.html',{'coupon':coupon1})
    else:
        return redirect(coupon)


def delete_coupon(request, id):
    if request.user.is_authenticated:
        coupon= Coupon.objects.get(id=id)
        coupon.delete()
        messages.success(request, f"Deleted brand {coupon.code} successfully.")
        return redirect(brand_manage)
    return redirect(adminHome)

def banner(request):
    if request.user.is_authenticated:
        banner = Banner.objects.all() 
        return render(request,'banner.html',{'banner':banner})
        

def add_banner(request):
    if request.method == 'POST':
        title1 = request.POST['title1']
        title2 = request.POST['title2']
        image1 = request.FILES['image1']
        tag = request.POST['tag']
        banner1 = Banner.objects.create(title1=title1, title2=title2, image1=image1, tag=tag)
        return redirect(banner)
    else:
        return render(request, 'add_banner.html')
    

def edit_banner(request,id):
    if request.user.is_authenticated:
        banner_1 = Banner.objects.get(id=id)
        if request.method == 'POST':
            title1 = request.POST['title1']
            title2 = request.POST['title2']
            image1 = request.FILES.get('image1')
            tag = request.POST['tag']

            banner_1.title1 = title1
            banner_1.title2 = title2
            banner_1.tag = tag
            if image1:
                banner_1.image1 = image1
            banner_1.save()
            messages.success(request, "Banner Updated")
            return redirect(banner)

        return render(request,'edit_banner.html',{'banner':banner_1})
    return redirect(banner)



def delete_banner(request,id):
    if request.user.is_authenticated:
        banner1= Banner.objects.get(id=id)
        banner1.delete()
        messages.success(request, f"Deleted brand successfully.")
        return redirect(banner)
    return redirect(adminHome)


def category_sales_report(request):
    # Get all the order items and group them by product category
    order_items_by_category = OrderItem.objects.values('product__category').annotate(total_sales=Sum('product_price'))

    # Get the sales for each category
    category_sales = {}
    for item in order_items_by_category:
        category = item['product__category']
        sales = item['total_sales']
        category_sales[category] = sales

    # Create the data for the graph
    data = {
        'labels': list(category_sales.keys()),
        'values': list(category_sales.values()),
    }

    return JsonResponse(data)
