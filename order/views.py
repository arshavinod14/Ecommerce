import datetime
from decimal import Decimal
import os
import random
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils import timezone
from product.views import check_out
import razorpay
from store.views import index
from .models import Order,OrderItem
from product.models import CartItems, Coupon
from store.models import Address,Account
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


# @cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required
def place_order(request):
    print("qwwfwer",request.POST.get)

    if request.method == 'POST':
        if 'saveaddress' in request.POST:
            print("helllooo from placeorder")
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
        else:
            neworder = Order()
            neworder.user = request.user
            neworder.address = Address.objects.get(pk=request.POST['address'])
            print(neworder.address)
            neworder.payment_method = request.POST.get('payment_method')
            print(neworder.payment_method)

            now = timezone.now()
            ord2 = str(datetime.now()) + str(request.user.id) + str(random.randint(0, 100))
            ord1 = ord2.translate({ord(':'): None, ord('-'): None, ord(' '): None, ord('.'): None}) 
            neworder.order_id = ord1
            if not neworder.address:
                return redirect('check_out')
            
            total_price = request.session.get('new_total_price', Decimal(0))  
            print("new_total_price",total_price)
            neworder.total_price = total_price
            neworder.save()


            neworderitems = CartItems.objects.filter(user=request.user)
            for item in neworderitems:
                OrderItem.objects.create(
                    order=neworder,
                    product=item.product,
                    product_price=item.unit_price * item.quantity,
                    quantity=item.quantity
                )

            CartItems.objects.filter(user=request.user).delete()
            return redirect('checking_confirm')
    return redirect("check_out")





def order_detail(request):
    order = Order.objects.filter(user=request.user).order_by('-order_at')  #- -> it will reverse the orders
    cart_items = CartItems.objects.filter(user=request.user)
    order_items = OrderItem.objects.all()
    
    count = cart_items.count()
    context = {
                'count':count,
                'order':order,
                'order_items':order_items,
                }
    return render(request, 'order_details.html',context)  



# def order_cancel(request, id):
#     order = Order.objects.get(id=id)
#     if order.status and order.delivery_status == 'P':
#         Order.objects.filter(id=id).update(status=False, delivery_status='C')

#     return redirect(order_detail)
def order_cancel(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return HttpResponse("Invalid order id.")
    
    if order.status and order.delivery_status == 'Pending':
        order.status = False
        order.delivery_status = 'Cancelled'
        messages.success(request, "Order canceled.")
        order.save()
        return redirect('order_detail')
    else:
        messages.error(request, "Order already canceled.")
        return redirect('order_detail')
    
def order_return(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return HttpResponse("Invalid order id.")
    
    if order.status and order.delivery_status == 'Delivered':
        order.status = False
        order.delivery_status = 'Returned'
        messages.success(request, "Order Returned.")
        order.save()
        return redirect('order_detail')
    else:
        messages.error(request, "Order already returned.")
        return redirect('order_detail')



def checking_confirm(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).order_by('-order_at').first()
        # if not order:
        #     return HttpResponse('You have not placed any orders yet.')
        order_items = OrderItem.objects.filter(order=order)
        now = datetime.now()
        context = {
            'order' : order,
            'now' :now,
            'order_items':order_items,
        }
        request.session['coupon'] = "Apply coupon"
        return render(request,'order_confirmation.html',context) 


def invoice(request,id):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).get(id=id)
        order_items = OrderItem.objects.filter(order=order)
        now = datetime.now()
        context = {
            'order':order,
            'now':now,
            'order_items':order_items,
        }
    return render(request,'invoice.html',context)

# @csrf_exempt
# def success(request):
#     print("wwwdedfd")
#     response = request.POST
#     print(response)  
#     params_dict = {
#         'razorpay_payment_id': response['razorpay_payment_id'],
#         'razorpay_order_id': response['razorpay_order_id'],
#         'razorpay_signature': response['razorpay_signature']
#     }
    
#     client = razorpay.Client(auth=("rzp_test_ZOq0MfvSYjUCuM", "ZyYHRwEp3cxBUpQndLnJKy9S"))
#     try:
#         client.utility.verify_payment_signature(params_dict)
#         print("ffffffff",request.POST)
#         neworder = Order()
#         neworder.user = request.user
#         print("ggggggggggggggg",request.session.get('address'))
#         neworder.address = Address.objects.get(pk=request.session.get('address'))
        
#         neworder.payment_method = '2'

#         now = timezone.now()
#         ord2 = str(datetime.now()) + str(request.user.id) + str(random.randint(0, 100))
#         ord1 = ord2.translate({ord(':'): None, ord('-'): None, ord(' '): None, ord('.'): None}) 
#         neworder.order_id = ord1
#         if not neworder.address:
#             return redirect('check_out')


#         # total_price = request.session.get('total_price', Decimal(0))  
#         # print("total_price",total_price)
#         # neworder.total_price = total_price
#         neworder.save()


#         neworderitems = CartItems.objects.filter(user=request.user)
#         for item in neworderitems:
#             OrderItem.objects.create(
#                 order=neworder,
#                 product=item.product,
#                 product_price=item.unit_price * item.quantity,
#                 quantity=item.quantity
#             )

#         CartItems.objects.filter(user=request.user).delete()
#         return checking_confirm(request)
#     except Exception as e:
#         print("jjjjjjjjjjjjjjj",e)
#         return render(request, 'checkout.html', context={'status': False})
#     return render(request, 'checkout.html')

# def get_add(request):
#     print("wwqqqqqq")
#     if request.method == 'POST':
#         print("rrrrr")
#         request.session['address'] = request.POST['address']
#         print("dddddddddddddddddddddd",request.session['address'])
#         return redirect('checkout')
#     return check_out(request)


from django.shortcuts import render, redirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

@csrf_exempt
def success(request):
    print("wwwdedfd")
    response = request.POST
    print(response)  
    params_dict = {
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    razorpay_key_id = os.getenv('RAZORPAY_KEY_ID')
    razorpay_key_secret =os.getenv('RAZORPAY_KEY_SECRET')
    
    client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
    try:
        client.utility.verify_payment_signature(params_dict)
        print("ffffffff",request.POST)
        neworder = Order()
        neworder.user = request.user
        address_pk = request.session.get('address')
        print(address_pk)
        
        try:
            neworder.address = Address.objects.get(pk=address_pk)
        except ObjectDoesNotExist:
    
            return redirect('check_out', error='Address not found')

        neworder.payment_method = 'RAZORPAY'

        now = timezone.now()
        ord2 = str(datetime.now()) + str(request.user.id) + str(random.randint(0, 100))
        ord1 = ord2.translate({ord(':'): None, ord('-'): None, ord(' '): None, ord('.'): None}) 
        neworder.order_id = ord1
        if not neworder.address:
            return redirect('check_out')


        total_price = request.session.get('new_total_price', Decimal(0))  
        print("total_price",total_price)
        neworder.total_price = total_price
        neworder.save()


        neworderitems = CartItems.objects.filter(user=request.user)
        for item in neworderitems:
            OrderItem.objects.create(
                order=neworder,
                product=item.product,
                product_price=item.unit_price * item.quantity,
                quantity=item.quantity
            )

        CartItems.objects.filter(user=request.user).delete()
        return checking_confirm(request)
    except Exception as e:
        print("jjjjjjjjjjjjjjj",e)
        return render(request, 'checkout.html', context={'status': False})

def get_add(request):
    print("wwqqqqqq")
    if request.method == 'POST':
        print("rrrrr")
        address = request.POST.get('address')
        print(address)
        request.session['address'] = address
        print("dddddddddddddddddddddd",request.session['address'])
        # return redirect('success')
    return check_out(request)




# def delete(request):
#     Order.objects.get(id=1).delete()
#     Order.objects.get(id=2).delete()
#     Order.objects.get(id=3).delete()

   
#     return redirect(index)


# from django.shortcuts import render, redirect
# from .models import Coupon

# def redeem_coupon(request):
#     if request.method == 'POST':
#         coupon_code = request.POST['coupon_code']
#         try:
#             coupon = Coupon.objects.get(code=coupon_code)
#             if coupon.is_valid() and not coupon.is_expired() and coupon.has_usage_left():
#                 # Check if the cart or order total meets the minimum purchase amount
#                 # (Implement your own logic here based on your application)
#                 # Example:
#                 min_purchase_amount = coupon.min_purchase_amount
#                 # cart_total = get_cart_total() or get_order_total()
#                 # if cart_total >= min_purchase_amount:
#                 #     Apply discount to the cart or order
#                 #     discount = coupon.discount
#                 #     cart.total -= (cart.total * discount / 100)
#                 #     cart.save()
#                 #     coupon.increment_usage()
#                 #     return redirect('checkout_success')
#                 # else:
#                 #     return render(request, 'coupon/redeem.html', {'error_message': 'Minimum purchase amount not met.'})
#             else:
#                 return render(request, 'coupon/redeem.html', {'error_message': 'Coupon is invalid, expired, or has no usage left.'})
#         except Coupon.DoesNotExist:
#             return render(request, 'coupon/redeem.html', {'error_message': 'Coupon not found.'})
#     else:
#         return render(request, 'coupon/redeem.html')



# <!-- coupon/redeem.html -->
# <form method="post">
#     {% csrf_token %}
#     <input type="text" name="coupon_code" placeholder="Enter coupon code">
#     <input type="number" name="min_purchase_amount" placeholder="Enter minimum purchase amount">
#     <button type="submit">Redeem</button>
# </form>

# {% if error_message %}
#     <p>{{ error_message }}</p>
# {% endif %}
