import datetime
from decimal import Decimal
import random
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.utils import timezone
from .models import Order, Payment,OrderItem
from product.views import check_out
from product.models import CartItems,Product
from store.models import Address
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views.decorators.cache import cache_control


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
            messages.success(request, "Your order has been placed successfully!")
        # Clear the session variables
        # del request.session['address']
        # del request.session['total_price']
            return HttpResponseRedirect("/?no_cache=1")
        # return redirect('/')
    return redirect("check_out")


def order_detail(request):
    order = Order.objects.filter(user=request.user)
    cart_items = CartItems.objects.filter(user=request.user)
    order_items = OrderItem.objects.all()
    
    count = cart_items.count()
    context = {
                'count':count,
                'order':order,
                'order_items':order_items,
                }
    return render(request, 'order_details.html',context)  

# def order_detail(request):
#     Order.objects.get(id=7).delete()
#     return redirect("check_out")




# def order_cancel(request, id):
#     order = Order.objects.get(id=id)
#     if order.status and order.delivery_status == 'P':
#         Order.objects.filter(id=id).update(status=False)

#     return redirect(order_detail)



def order_cancel(request, id):
    order = Order.objects.get(id=id)
    if order.status and order.delivery_status == 'P':
        Order.objects.filter(id=id).update(status=False, delivery_status='C')

    return redirect(order_detail)

