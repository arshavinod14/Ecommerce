from django.shortcuts import get_object_or_404, render,redirect
from product.forms import *
from .models import CartItems, Product,Category, Size
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

def product_view(request):
    products = Product.objects.all()
    category = Category.objects.all()

    size = Size.objects.all()
    brand = Brand.objects.all()
    count_p = Product.objects.all().count()
    cart_items = CartItems.objects.filter(user=request.user)
    count = cart_items.count()
    context = {
        'category': category,
        'products': products,
        'size': size,
        'count_p':count_p,
        'count':count,
        'brand':brand,

    }
    print(products)
    return render(request, 'products.html', context)

def single_product(request, id):
    product = Product.objects.get(id=id)
    sizes = Size.objects.all()
    form = CartItemsForm()
    cart_items = CartItems.objects.filter(user=request.user)
    count = cart_items.count()
    context = {'product': product, 'sizes': sizes, 'form': form,'count':count}
    
    if request.method == 'POST':
        size_id = request.POST.get('size')
        size = Size.objects.get(id=size_id)
        cart_item = CartItems(product=product, size=size)
        cart_item.save()
        messages.success(request, 'Item added to cart')
    
    return render(request, 'single-product-details.html', context)


def add_to_cart(request, id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id)
        cart_item = CartItems.objects.filter(product=product, user=request.user)
        if cart_item.exists():
            cart_item = cart_item.first()
            cart_item.quantity += 1
            cart_item.total_price = cart_item.quantity * cart_item.unit_price
            cart_item.save()
        else:
            cart_item = CartItems.objects.create(product=product, user=request.user, quantity=1, unit_price=product.price, total_price=product.price)

        return redirect('product_view')
    else:

        messages.error(request, "Please Login ")
        return render(request,'index.html')

@login_required(login_url=loginacc)
def view_cart(request):
    if request.user.is_authenticated:
        cart_items = CartItems.objects.filter(user=request.user)
        count = cart_items.count()
        total_price = 0
        for item in cart_items:
            total_price += item.total_price
        return render(request, 'cart.html', {'cart_items': cart_items, 'count': count, 'total_price': total_price})
    else:
        messages.error(request, "Please Login ")
        return render(request,'index.html')



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
    # else:
    #     messages.error(request, "Please Login ")
    #     return render(request,'index.html')



def remove_cart(request, id):
    if request.user.is_authenticated:
        CartItems.objects.get(id=id).delete()
        #count = CartItems.objects.filter(user_id=request.user.id).count()
        # request.session['count'] = count
        return redirect('view_cart')


def check_stock(request):
    item_id = request.GET.get('item_id')
    item = CartItems.objects.get(id=item_id)
    stock_level = item.product.stock
    data = {'stock_level': stock_level}
    return JsonResponse(data)

@login_required(login_url=loginacc)
def check_out(request):
    ad = Address.objects.filter(user=request.user)
    selected_address = None
    selected_address_id = None
    total_price = 0


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

    cart_items = CartItems.objects.filter(user=request.user)
    count = cart_items.count()

    context = {'cartitems': cart_items, 'total_price': total_price, 'count': count, 'ad': ad, 'selected_address': selected_address}
    return render(request, 'checkout.html', context)


def women_product(request):
    women_category = Category.objects.get(name="Women's Fashion")
    products = Product.objects.filter(category=women_category)
    size = Size.objects.all()
    brand = Brand.objects.all()
    count_p = Product.objects.filter(category=women_category).count()
    cart_items = CartItems.objects.filter(user=request.user)
    count = cart_items.count()
    context = {
        'women_category': women_category,
        'products': products,
        'size': size,
        'count_p':count_p,
        'count':count,
        'brand':brand,
    }
    print(products)
    return render(request, 'products.html', context)


def men_product(request):
    men_category = Category.objects.get(name="Men's Fashion")
    products = Product.objects.filter(category=men_category)
    size = Size.objects.all()
    brand = Brand.objects.all()
    count_p = Product.objects.filter(category=men_category).count()
    cart_items = CartItems.objects.filter(user=request.user)
    count = cart_items.count()
    context = {
        'men_category': men_category,
        'products': products,
        'size': size,
        'count_p':count_p,
        'count':count,
        'brand':brand,
    }
    print(products)
    return render(request, 'products.html', context)

def category_products(request, category_slug, subcategory_slug):
    brand = Brand.objects.all()
    print("ggggggggggg")
    category = get_object_or_404(Category, slug=category_slug)
    print(category)
    subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=category)
    print(subcategory)
    products = Product.objects.filter(subcategory=subcategory)
    print(products)
    context = {
        'category': category,
        'subcategory': subcategory,
        'products': products,
        'brand':brand,
    }
    return render(request, 'products.html', context)


def sort_products(request):
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_asc':
        products = Product.objects.order_by('price')
    elif sort_by == 'price_desc':
        products = Product.objects.order_by('-price')
    else:
        products = Product.objects.all()

    count_p = Product.objects.all().count()
    brand = Brand.objects.all()
    context = {'products': products,'count_p':count_p,'brand':brand,}
    return render(request, 'products.html', context)


