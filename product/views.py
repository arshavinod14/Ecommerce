import json
from django.shortcuts import render,redirect
from product.forms import *
from .models import CartItems, Coupon, Product,Category, Size,GuestCart
from store.views import loginacc
from django.http import  JsonResponse
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from store.models import Address
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import razorpay
from django.http import  JsonResponse, HttpResponseRedirect
from django.urls import reverse



def product_view(request):
    if not request.session.session_key:
        request.session.create()
    request.session['guest_key'] = request.session.session_key
    cart_items = GuestCart.objects.filter(user_ref=request.session['guest_key'])
    count = cart_items.count()

    products_list = Product.objects.all()
    category_filter = request.GET.get('category', None)
    request.session['category'] = category_filter
    subcategory_filter = request.GET.get('subcategory', None)
    request.session['subcategory'] = subcategory_filter
    if category_filter:
        products_list = Product.objects.filter(category=category_filter)
    if subcategory_filter:
        products_list = products_list.filter(subcategory=subcategory_filter)

    brand_filter = request.GET.get('brand', None)
    request.session['brand'] = brand_filter
    if brand_filter:
        products_list = products_list.filter(brand__name=brand_filter)

    paginator = Paginator(products_list, 5)  # Show 10 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)

    categories = Category.objects.all()
    s = []
    for category in categories:
        subcategories = SubCategory.objects.filter(category=category)
        subcategory_list = [{
            'id': subcategory.id,
            'name': subcategory.name
        } for subcategory in subcategories]
        s.append({
            'id': category.id,
            'name': category.name,
            'subcategories': subcategory_list
        })
    size = Size.objects.all()
    brand = Brand.objects.all()
    count_p = products_list.count()

    context = {
        'category_url': categories,
        'request': request,
        'url': request.GET,
        'categories': s,
        'category': category_filter or None,
        'products': products,
        'size': size,
        'count_p': count_p,
        'count': count,
        'brand': brand,
        'brand_filter': brand_filter,
    }
    return render(request, 'products.html', context)

def single_product(request, id):
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
            total_price += item.total_price


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
    if request.user.is_authenticated:
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
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('new_quantity')
        item = GuestCart.objects.get(id=item_id)
        item.quantity = new_quantity
        
        item.total_price = (item.unit_price * Decimal(item.quantity)).quantize(Decimal('0.00'))
        item.save()
        total_price = GuestCart.objects.filter(user_ref = request.session['guest_key']).aggregate(Sum('total_price'))
        return JsonResponse({ 'new_total_price': total_price['total_price__sum']})
    

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
            obj.applied_coupon_id = couponDetail.id
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

        
        request.session["new_total_price"] = str(new_total_price)


    order_currency = 'INR'
    client = razorpay.Client(
                        auth=('rzp_test_ZOq0MfvSYjUCuM', 'ZyYHRwEp3cxBUpQndLnJKy9S')
                    )
    payment = client.order.create({'amount': int(total_price)*100, 'currency': 'INR', 'payment_capture': 0})

    payment_id = payment['id']
    
    context = {'cartitems': cart_items, 'total_price': total_price, 'ad': ad, 'selected_address': selected_address,'payment_id':payment_id, "code": coupon}
    return render(request, 'checkout.html', context)

def changeQuantity(request):
    if request.method == 'POST' :
        proId = request.POST.get('productId')
        qty = request.POST.get('qty')
        count = request.POST.get('count')



def sort_products(request):
    sort_by = request.GET.get('sort_by')
    category = request.session.get('category') if request.session.get('category') else None
    subcategory = request.session.get('subcategory') if request.session.get('subcategory') else None
    brand_filter = request.session.get('brand') if request.session.get('brand') else None
    if sort_by == 'price_asc':
        if category:
            products = Product.objects.filter(category=category).order_by('price')
        elif subcategory:
            products = Product.objects.filter(subcategory=subcategory).order_by('price')
        elif brand_filter:
            products = Product.objects.filter(brand__name=brand_filter).order_by('price')
        else:
            products = Product.objects.order_by('price')
    elif sort_by == 'price_desc':
        if category:
            products = Product.objects.filter(category=category).order_by('-price')
        elif subcategory:
            products = Product.objects.filter(subcategory=subcategory).order_by('-price')
        elif brand_filter:
            products = Product.objects.filter(brand__name=brand_filter).order_by('-price')
        else:
            products = Product.objects.order_by('-price')
    else:
        if category:
            products = Product.objects.filter(category=category)
        elif subcategory:
            products = Product.objects.filter(subcategory=subcategory)
        elif brand_filter:
            products = Product.objects.filter(brand__name=brand_filter)
        else:
            products = Product.objects.all()

    count_p = products.count()
    brand = Brand.objects.all()
    context = {'products': products,
            'count_p': count_p,
            'brand': brand,
            'request': request,
            'url': request.GET,
            'brand_filter': brand_filter}
    return render(request, 'products.html', context)


