from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from admin_side.models import *
from .models import *
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import random
from .form import *
from django.core.exceptions import ObjectDoesNotExist
from order.models import *
import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q



from .models import *
# Create your views here.



def us_products(request):
    sizes=Size.objects.all()
    category = Category.objects.all()
    brand=Brand.objects.all()
    prod = Product.objects.all()
    products = ProductVarient.objects.all()
    for variants in products:
        products.sizes = sizes
        offer_price = round(variants.price -( variants.price *(variants.offer/100 )))if variants.offer else variants.price
        variants.offer_price = offer_price
    
    context={
             'prod': prod,
             'category':category,
             
             'products':products,
             'sizes':sizes,
             'brand':brand,
             }
    return render(request,'main/products.html',context)


def home(request): 
    products = Product.objects.all()
    variant = Variant.objects.all()
    paginator = Paginator(variant, 8)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr)
    dict_product={
            'var': variant,
            'page_obj':page_obj
            }
    return render(request, 'main/index.html', dict_product)

from django.shortcuts import get_object_or_404

def product_details(request, id): 
    # rating = [ 'Poor', 'Fair', 'Average', 'Good', 'Excellent']
    variant = Variant.objects.get(pk=id)
    # review=ProductReview.objects.filter(product=variant)
    product = get_object_or_404(Product, name=variant.product)
    img = Variant.objects.filter(product=product)
    
    size = Size.objects.filter(variant=variant)
    if not size:
        size = None
        
    dict_product={
        # 'review':review,
        # 'rating': rating,
        'var':Variant.objects.get(pk=id),
        'img':img,  
        'size':size,         
    }
        
    # variant = Variant.objects.get(pk=id)
    # product = get_object_or_404(Product, name=variant.product)
    # img = Variant.objects.filter(product=product)
    # print(img,'--------------------------------------------------')
    
    # size = Size.objects.filter(variant=variant)
    # dict_product={
    #     'var':Variant.objects.get(pk=id),
    #     'img':img,  
    #     'size':size,         
    #               }
    return render(request, 'main/product_details.html', dict_product)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def addtocart(request, variant_id):
        if request.user.is_authenticated:
            if request.method == 'POST':
            # Get the current user
                current_user = request.user
                
                # Get the selected quantity of the product
                try :
                    s = request.POST['size']
                except :
                    messages.error(request, "Please select the size and try again.")
                    return redirect(product_details,variant_id)
                variant = get_object_or_404(Variant, id=variant_id)
                size = Size.objects.filter(variant=variant, size=s).first()
                quantity = request.GET.get('quantity')
                if quantity is None:
                    product_quantity = 1
                else:
                    product_quantity = int(quantity)

                # Get the selected variant and size

                # Check if the item already exists in the cart
                item_exists = CartItem.objects.filter(user=current_user, product=variant, size=size).exists()
                if item_exists:
                    item = CartItem.objects.get(user=current_user, product=variant, size=size)
                    quantity_expected = item.quantity + product_quantity
                    
                    if size.stock >= quantity_expected:
                            item.quantity = item.quantity + product_quantity
                            item.save()
                            messages.success(request, f"{variant.product} ({size.size}) are added to the cart.")     
                    else:
                        item.quantity = size.stock
                        item.save()
                        messages.info(request, f"{size.stock} items left. All of them are added to the cart.")
                else:
                    if size.stock >= product_quantity:
                        CartItem.objects.create(user=current_user, product=variant, size=size, quantity=product_quantity)
                        messages.success(request, f"{variant.product} ({size.size}) added to cart!")
                    else:
                        product_quantity = size.stock
                        CartItem.objects.create(user=current_user, product=variant, size=size, quantity=product_quantity)
                        messages.info(request, f"{size.stock} items left. All of them are added to the cart.")

                return redirect('cart')    
        else:
            messages.warning(request, "Please log in to add items to cart.")
            return redirect('login')


def viewcart(request):
    if request.user.is_authenticated:
        current_user = request.user

        items = CartItem.objects.filter(user_id=current_user.id).order_by('id')
        cart_items = []
        total = 0
        for cart_item in items:
            s = cart_item.size
            product = get_object_or_404(Variant, id=cart_item.product.id)
            size = Size.objects.filter(variant=product, size=s).first()
            quantity = cart_item.quantity
            price = product.price*quantity
            cart_items.append({'product':product,'quantity':quantity,'price':price,'size':size}) 
            if size.stock == 0:
                pass
            else:
                total += price   
        context = { 'cart_items': cart_items, 'total': total }

    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect('login')
    return render(request, 'main/cart.html',context)


def removecartproduct(request,product_id):
    current_user = request.user
    product=get_object_or_404(Variant,id=product_id)
    cart_item=CartItem.objects.get(user_id=current_user.id,product_id=product.id)
    cart_item.delete()
    return redirect(viewcart)

def addcartitem(request,product_id):
    if request.user.is_authenticated :
        current_user=request.user
        product = get_object_or_404(Variant, id=product_id)
        item = CartItem.objects.get(user_id=current_user.id, product=product)
        s = item.size
        size = Size.objects.filter(variant=product, size=s).first()

        
        item.quantity = item.quantity + 1
        if (size.stock>=item.quantity):
            item.save()
            return redirect(viewcart)
        else:
            messages.warning(request,"Product Out Of Stock...! Can't be added to cart")
            return redirect(viewcart)

    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect('login')
    
def removecartitem(request,product_id):
    current_user = request.user
    product = get_object_or_404(Variant, id=product_id)

    cart_items = CartItem.objects.filter(user_id=current_user.id, product=product)
    print(cart_items)
    for cart_item in cart_items:
        if cart_item.quantity == 1:
            cart_item.delete()  # remove the item from the cart if the quantity is 1
        else:
            cart_item.quantity -= 1
            cart_item.save()  # decrement the quantity by 1
    return redirect(viewcart)



def userwishlist(request):
    user = request.user
    witems=wishlist.objects.filter(user_id=user.id)
    context={
        'witems':witems,
    }
    return render(request,'main/wishlist.html',context)

def add_to_wishlist(request,product_id):
    if request.user.is_authenticated:
        product = Variant.objects.get(id=product_id)
        user = request.user
        if wishlist.objects.filter(product=product,user_id=user.id).exists():
            messages.warning(request, "Product already exist in wishlist")
            return redirect(userwishlist)
            
        else:
            wishlist.objects.create(product=product,user_id=user.id)
            messages.success(request,"Product added to wishlist")
            return redirect(userwishlist)
            
    else:
        messages.warning(request, "Please log in to add items to wishlist.")
        return redirect('login')
    
def remove_from_wishlist(request,product_id):
    user = request.user
    wishItem=wishlist.objects.get(product_id=product_id,user_id=user.id)
    wishItem.delete()
    return redirect(userwishlist)

def filterplace(request, cid):
    if cid == 0:
        products = Product.objects.all()
        variant = Variant.objects.all()
    else:
        category = get_object_or_404(Category, id=cid)
        variant = Variant.objects.filter(category=category)

    # Get the min and max price values from the request's GET parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Set default values for min_price and max_price if they are not present in GET parameters
    if not min_price:
        min_price = "100"  # Set default min price value as string
    if not max_price:
        max_price = "3000"  # Set default max price value as string

    # Filter the products by price if the min_price and max_price GET parameters exist
    if min_price and max_price:
        min_price = min_price.replace('$', '')
        max_price = max_price.replace('$', '')
        if min_price < '99' and max_price<'100':
            max_price ="3000"
            min_price ="100"            
            variant = variant.filter(Q(price__gte=min_price) & Q(price__lte=max_price))
            
   
    categories = Category.objects.all()
    paginator = Paginator(variant, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    dict_product = {
        'categories': categories,
        'var': variant,
        'page_obj': page_obj,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'main/filterplace.html', dict_product)





def category(request, cid):
    if cid == 0:
        products = Product.objects.all()
        variant = Variant.objects.all()
    else:
        category = get_object_or_404(Category, id=cid)
        variant = Variant.objects.filter(category=category)

    categories = Category.objects.all()
    paginator = Paginator(variant, 6)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr)
    dict_product={
            'categories': categories,
            'var': variant,
            'page_obj':page_obj
            }
    return render(request, 'main/filterplace.html', dict_product) 



def search(request):
    keyword = request.GET.get('name')
    products = Variant.objects.filter(Q(product__name__icontains=keyword) | Q(color__icontains=keyword)).order_by('created')
    categories = Category.objects.all()
    paginator = Paginator(products, 6)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr) 
    dict_product = {
        'categories': categories,
        'var': products,
        'page_obj':page_obj
    }
    return render(request, 'main/filterplace.html', dict_product)




@login_required(login_url='login')
def checkout(request):
    current_user = request.user
    user = Customer.objects.get(id=current_user.id)

    address = AddressDetails.objects.filter(user=user)
    
    items = CartItem.objects.filter(user_id=current_user.id).order_by('id')
    cart_items = []
    total = 0
    for cart_item in items:
        s = cart_item.size
        print(s,"size of s in viewcart............................................")
        product = get_object_or_404(Variant, id=cart_item.product.id)
        size = Size.objects.filter(variant=product, size=s).first()
        quantity = cart_item.quantity
        price = product.price*quantity
        cart_items.append({'product':product,'quantity':quantity,'price':price}) 
        if size.stock == 0:
            pass
        else:
            shipping = 50
            total += price   
            tws =total+shipping

    context = { 
        'cart_items': cart_items, 
        'st': total, 
        'shp' : shipping, 
        'tws': tws, 
        'price':price, 
        'user': user,
        'address': address ,
    }
    return render(request, 'main/checkout.html',context)



@login_required(login_url='login')
def myaccount(request):
  
    return render(request,'main/myaccount.html')
  
@login_required(login_url='login')
def orderbook(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'main/orders.html', {'orders': orders})
  
@login_required(login_url='login')
def viewOrder(request, id):
    order =Order.objects.filter(id=id,user=request.user).first()
    orderitems = OrderProduct.objects.filter(order=order)

    context={
        'order': order,
        'orderitems':orderitems,
    }
    return render(request,'main/orderview.html',context)

@login_required(login_url='login')
def razorPayCheck(request):
   total=0
#    coupon_discount =0
   amountToBePaid = 0
   current_user=request.user
   cart_items=CartItem.objects.filter(user_id=current_user.id)
   if cart_items:
      for cart_item in cart_items:
         total+=(cart_item.product.price*cart_item.quantity)
      tax=50
      grand_total=total+tax
      grand_total = round(grand_total,2)
      amountToBePaid = grand_total
      print()
      return JsonResponse({
         'grand_total' : grand_total,
        #  'coupon': coupon,
        #  'coupon_discount':coupon_discount,
         'amountToBePaid':amountToBePaid
      })
   else:
      return redirect('filterplace',0)
  
