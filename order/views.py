import datetime
from decimal import Decimal
import random
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.contrib import messages
from django.utils import timezone

from store.views import index
from .models import Order,OrderItem
from product.models import CartItems
from store.models import Address,Account
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone



# @cache_control(no_cache=True, must_revalidate=True,no_store=True)
@login_required
def place_order(request):
    print("qwwfwer",request.POST.get)

    if request.method == 'POST':
        if 'saveaddress' in request.POST:
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
            neworder.payment_method = request.POST.get('payment_method')

            now = timezone.now()
            ord2 = str(datetime.now()) + str(request.user.id) + str(random.randint(0, 100))
            ord1 = ord2.translate({ord(':'): None, ord('-'): None, ord(' '): None, ord('.'): None}) 
            neworder.order_id = ord1
            if not neworder.address:
                return redirect('check_out')


            total_price = request.session.get('total_price', Decimal(0))  
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
        order.save()
        return redirect('order_detail')
    else:
        messages.error(request, "Order cannot be canceled.")
        return redirect('order_detail')
    



def checking_confirm(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user).order_by('-order_at').first()
        if not order:
            return HttpResponse('You have not placed any orders yet.')
        order_items = OrderItem.objects.filter(order=order)
        now = datetime.now()
        context = {
            'order' : order,
            'now' :now,
            'order_items':order_items,
        }
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




# def delete(request):
#     Order.objects.get(id=1).delete()
#     Order.objects.get(id=2).delete()
#     Order.objects.get(id=3).delete()
#     Order.objects.get(id=4).delete()
#     Order.objects.get(id=5).delete()
#     Order.objects.get(id=6).delete()
#     Order.objects.get(id=7).delete()
#     Order.objects.get(id=8).delete()
   
#     return redirect(index)


