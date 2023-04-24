from product.models import CartItems

def count(request):
    if request.user.is_authenticated:
        cart_items = CartItems.objects.filter(user=request.user)
        count = cart_items.count()
    else:
        count = 0
    return {'count': count}
