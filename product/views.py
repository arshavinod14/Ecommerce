import json
from django.shortcuts import get_object_or_404, render,redirect
from product.forms import *
from .models import CartItems, Coupon, Product,Category, Size,GuestCart
from store.views import loginacc
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from store.models import Address
from order.models import Order,OrderItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import razorpay
from django.db.models import Q


# def product_view(request):
#     if request.user.is_authenticated:
#         products = Product.objects.all()
#         category = Category.objects.all()
#         size = Size.objects.all()
#         brand = Brand.objects.all()
#         count_p = Product.objects.all().count()
#         cart_items = CartItems.objects.filter(user=request.user)
#         count = cart_items.count()
#         context = {
#             'category': category,
#             'products': products,
#             'size': size,
#             'count_p':count_p,
#             'count':count,
#             'brand':brand,
#         }
#     # print(products)
#         return render(request, 'products.html', context)
    
#     products = Product.objects.all()
#     category = Category.objects.all()
#     guest = {
#         'products':products,
#         'category':category,
#     }
#     return render(request,'products.html',guest)


def product_view(request):
    if request.user.is_authenticated:
        cart_items = CartItems.objects.filter(user=request.user)
        count = cart_items.count()
    else:
        if not request.session.session_key:
            request.session.create()
        request.session['guest_key']=request.session.session_key
        cart_items = GuestCart.objects.filter(user_ref = request.session['guest_key'])
        count = cart_items.count()


    products_list = Product.objects.all()
    category = request.GET.get('category',None)
    request.session['category'] = category
    subcategory = request.GET.get('subcategory',None)
    request.session['subcategory'] = subcategory
    if category:
        products_list = Product.objects.filter(category=category)
    if subcategory:
        products_list = Product.objects.filter(subcategory=request.GET.get('subcategory'))
        
    paginator = Paginator(products_list, 5) # Show 10 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)

    category = Category.objects.all()
    s = []
    for i in category:
        s.append({
            'id':i.id,
            'name':i.name,
            'subcategory':SubCategory.objects.filter(category=i.id).values()
        })
    size = Size.objects.all()
    brand = Brand.objects.all()
    count_p = Product.objects.all().count()
    
    
    print("dddddddddddddd",request.GET)
    context = {
        'category_url':category,
        'request': request,
        'url' : request.GET,
        'category': s,
        'products': products,
        'size': size,
        'count_p': count_p,
        'count': count,
        'brand':brand,
    }
    print(request.GET)
    return render(request, 'products.html', context)


def single_product(request, id):
    if request.user.is_authenticated:
        cart_items = CartItems.objects.filter(user=request.user)
        count = cart_items.count()
    else:
        if not request.session.session_key:
            request.session.create()
        request.session['guest_key']=request.session.session_key
        cart_items = GuestCart.objects.filter(user_ref = request.session['guest_key'])
        count = cart_items.count() 

    product = Product.objects.get(id=id)
    sizes = Size.objects.all()

    if request.method == 'POST':
        size_id = request.POST.get('size')
        size = Size.objects.get(id=size_id)
        cart_item = CartItems(product=product, size=size)
        cart_item.save()
        messages.success(request, 'Item added to cart')
    context = {
        'count':count,
        'product':product,
        'sizes':sizes,
        'cart_items':cart_items,
    }
    return render(request, 'single-product-details.html', context)


def add_to_cart(request, id):
    product = Product.objects.get(id=id)
    if request.user.is_authenticated:
        cart_item = CartItems.objects.filter(product=product, user=request.user)
        if cart_item.exists():
            cart_item = cart_item.first()
            cart_item.quantity += 1
            cart_item.total_price = cart_item.quantity * cart_item.unit_price
            cart_item.save()
        else:
            cart_item = CartItems.objects.create(product=product, user=request.user, quantity=1, unit_price=product.price, total_price=product.price)
        cart_items = CartItems.objects.filter(user=request.user)
        count = cart_items.count()
        return JsonResponse({'message': 'Product added to cart.', 'success': True, 'count': count})
    else:
        if not request.session.session_key:
            request.session.create()
        request.session['guest_key']=request.session.session_key
        guest_cart = GuestCart.objects.filter(product=product,user_ref = request.session['guest_key'])
        if guest_cart.exists():
            guest_cart = guest_cart.first()
            guest_cart.quantity += 1
            guest_cart.total_price = guest_cart.quantity * guest_cart.unit_price
            guest_cart.save()
        else:
            guest_cart = GuestCart.objects.create(product=product,user_ref = request.session['guest_key'],quantity = 1,unit_price=product.price,total_price=product.price)
        guest_cart = GuestCart.objects.filter(user_ref = request.session['guest_key'])
        count = guest_cart.count()
        return JsonResponse({'message': 'Product added to cart.', 'success': True, 'count': count})



def view_cart(request):
    if request.user.is_authenticated:
        cart_items = CartItems.objects.filter(user=request.user)

        count = cart_items.count()
        total_price = 0
        for item in cart_items:
            # print(item.applied_coupon.code)
            total_price += item.total_price
        print(cart_items)
        

        # code = cart_items[0].applied_coupon.code if cart_items and cart_items[0].applied_coupon else 'Apply Coupon'

        return render(request, 'cart.html', {'cart_items': cart_items, 'count': count, 'total_price': total_price})
    else:
        if not request.session.session_key:
            request.session.create()
        request.session['guest_key'] = request.session.session_key
        guest_cart = GuestCart.objects.filter(user_ref=request.session['guest_key'])
        count = guest_cart.count()
        total_price = 0
        for item in guest_cart:
            total_price += item.total_price
        return render(request, 'cart.html', {'cart_items': guest_cart, 'count': count, 'total_price': total_price})


@csrf_exempt
def update_quantity(request):
    print("aaaaaaaa")
    if request.user.is_authenticated:
        print('sssssssssssssss')
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('new_quantity')
        item = CartItems.objects.get(id=item_id)
        item.quantity = new_quantity
        #item.total_price = item.unit_price * item.quantity
        item.total_price = (item.unit_price * Decimal(item.quantity)).quantize(Decimal('0.00'))
        item.save()
        total_price = CartItems.objects.filter(user=request.user).aggregate(Sum('total_price'))
        return JsonResponse({ 'new_total_price': total_price['total_price__sum']})
    

    else:
        print("eeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('new_quantity')
        item = GuestCart.objects.get(id=item_id)
        item.quantity = new_quantity
        
        item.total_price = (item.unit_price * Decimal(item.quantity)).quantize(Decimal('0.00'))
        item.save()
        total_price = GuestCart.objects.filter(user_ref = request.session['guest_key']).aggregate(Sum('total_price'))
        return JsonResponse({ 'new_total_price': total_price['total_price__sum']})
    






from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse


def remove_cart(request, id):
    if request.user.is_authenticated:
        CartItems.objects.get(id=id).delete()
        messages.success(request,'product removed from cart')
        return HttpResponseRedirect(reverse('view_cart'))
    else:
        GuestCart.objects.get(id=id).delete()
        messages.success(request,'product removed from cart')
        return HttpResponseRedirect(reverse('view_cart'))



def check_stock(request):
    if request.user.is_authenticated:
        item_id = request.GET.get('item_id')
        item = CartItems.objects.get(id=item_id)
        stock_level = item.product.stock
        data = {'stock_level': stock_level}
        return JsonResponse(data)
    else:
        item_id = request.GET.get('item_id')
        item = GuestCart.objects.get(id=item_id)
        stock_level = item.product.stock
        data = {'stock_level': stock_level}
        return JsonResponse(data)
    
# def apply_coupon(request):
#     if request.method == 'POST':
#         coupon = request.POST.get('coupon_code')
#         couponDetail = Coupon.objects.get(code=coupon)
#         cartDetails = CartItems.objects.filter(user=request.user)
#         total_price = 0
#         for obj in cartDetails:
#             discountAmount = (obj.total_price * Decimal(couponDetail.discount)) / 100
#             obj.total_price -= discountAmount
#             obj.applied_coupon = couponDetail
#             obj.save()
#             total_price += obj.total_price

#         return JsonResponse({'message': 'Coupon has been applied.', 'total_price': total_price})

def apply_coupon(request):
    if request.method == 'POST':
        coupon = request.POST.get('coupon_code')
        couponDetail = Coupon.objects.get(code=coupon)
        cartDetails = CartItems.objects.filter(user=request.user)
        request.session["coupon"] = couponDetail.code
        total_price = 0
        for obj in cartDetails:
            discountAmount = (obj.total_price * Decimal(couponDetail.discount)) / 100
            # obj.total_price -= discountAmount
            obj.discount = discountAmount
            obj.save()
            total_price = obj.total_price - obj.discount

        return JsonResponse({'message': 'Coupon has been applied.', 'total_price': total_price})


@login_required(login_url=loginacc)
def check_out(request):
    ad = Address.objects.filter(user=request.user)
    selected_address = None
    selected_address_id = None
    total_price = 0
    discount = 0
    coupon =  request.session.get('coupon') if request.session.get('coupon') else "Apply coupon"
    print("Coupon applied",coupon)
    new_total_price = 0



    cart_items = CartItems.objects.filter(user=request.user)
    for item in cart_items:
        total_price = total_price + item.unit_price * item.quantity
    request.session['total_price'] = str(total_price)

    
    if request.method == 'POST':
        selected_address_id = request.POST.get('selected_address_id')
        if selected_address_id:
            request.session['address_id'] = selected_address_id
            selected_address = Address.objects.get(id=selected_address_id)

    else:
        address_id = request.session.get('address_id')
        if address_id:
            try:
                selected_address = Address.objects.get(id=address_id)
            except Address.DoesNotExist:
                selected_address = None

        total_price = request.session.get('total_price')
        if total_price:
            total_price = Decimal(total_price)

        
        for item in cart_items:
            new_total_price += item.total_price - item.discount
        
        total_price = new_total_price

        print('apply coupon side', new_total_price)
        
        request.session["new_total_price"] = str(new_total_price)
        


    cart_items = CartItems.objects.filter(user=request.user)
    count = cart_items.count()

    order_currency = 'INR'
    print("dddd",int(total_price)*100)
    client = razorpay.Client(
                        auth=('rzp_test_ZOq0MfvSYjUCuM', 'ZyYHRwEp3cxBUpQndLnJKy9S')
                    )
    payment = client.order.create({'amount': int(total_price)*100, 'currency': 'INR', 'payment_capture': 0})

    payment_id = payment['id']
    
    context = {'cartitems': cart_items, 'total_price': total_price, 'count': count, 'ad': ad, 'selected_address': selected_address,'payment_id':payment_id, "code": coupon}
    return render(request, 'checkout.html', context)

def changeQuantity(request):
    if request.method == 'POST' :
        proId = request.POST.get('productId')
        qty = request.POST.get('qty')
        count = request.POST.get('count')
        print(proId, qty, count)



def sort_products(request):
    sort_by = request.GET.get('sort_by')
    category = request.session.get('category') if request.session.get('category') else None
    subcategory = request.session.get('subcategory') if request.session.get('subcategory') else None
    print(category)
    if sort_by == 'price_asc':
        if(category):
            products = Product.objects.filter(category=category).order_by('price')
        elif subcategory:
            products = Product.objects.filter(subcategory=subcategory).order_by('price')
        else:
            products = Product.objects.order_by('price')
    elif sort_by == 'price_desc':
        if category:
            products = Product.objects.filter(category=category).order_by('-price')
        elif subcategory :
            products = Product.objects.filter(subcategory=subcategory).order_by('-price')
        else:
            products = Product.objects.order_by('-price')
    else:
        products = Product.objects.all()

    count_p = Product.objects.all().count()
    brand = Brand.objects.all()
    category = Category.objects.all()
    context = {'products': products,'count_p':count_p,'brand':brand,'category':category}
    return render(request, 'products.html', context)


