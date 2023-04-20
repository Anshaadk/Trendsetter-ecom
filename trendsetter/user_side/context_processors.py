# from admin_side.models import *
# from user_side.models import *
# from .views import _cart_id

# def menu_links(request):
#     links = Category.objects.all()
#     return dict(links=links)



# def counter(request):
#   cart_count = 0
#   if 'admin' in request.path:
#     return {}
#   else:
#     try:
#       cart = Cart.objects.filter(cart_id=_cart_id(request))
#       if request.user.is_authenticated:
#         cart_items =CartItem.objects.all().filter(user=request.user)
#       else:
#         cart_items = CartItem.objects.filter(cart=cart[:1])
      
#       for cart_item in cart_items:
#         cart_count += cart_item.quantity
    
#     except Cart.DoesNotExist:
#       cart_count=0
      
#   return dict(cart_count=cart_count)

# def total(request):
#   cart_total = 0
#   if 'admin' in request.path:
#     return()
#   else:
#     try:
#       cart = Cart.objects.filter(cart_id=_cart_id(request))
#       if request.user.is_authenticated:
#         cart_items = CartItem.objects.filter(user=request.user)
#       else:
#         cart_items = CartItem.objects.filter(cart=cart[:1])
      
#       for cart_item in cart_items:
#         price_mult = int(cart_item.variations.all().values_list('price_multiplier')[0][0])
#         cart_total += int(cart_item.product.offer_price())*int(cart_item.quantity)*price_mult
            
#     except Cart.DoesNotExist:
#       cart_total=0
      
#   return dict(cart_total=cart_total)




# def stock_counter(request):
#     total_stock = Product.objects.filter(is_available=True).aggregate(total_stock=models.Sum('stock'))['total_stock'] or 0
#     return {'total_stock': total_stock}
