from product.models import CartItems, Category, SubCategory

def count(request):
    if request.user.is_authenticated:
        cart_items = CartItems.objects.filter(user=request.user)
        count = cart_items.count()
    else:
        count = 0
    return {'count': count}


def catsub(request):
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

    return {'categories':s,'category':category}