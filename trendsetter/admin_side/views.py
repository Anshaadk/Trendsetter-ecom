from django.shortcuts import render,redirect
from .models import *
from django.utils.text import slugify
from django.contrib import auth,messages
from user_side.views import *
from account.models import *
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from datetime import datetime,timedelta,date
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Cast
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from .form import *
from django.db.models import Sum, F
import razorpay


# from django.http import HttpResponse
# from django.template.loader import get_template




# Create your views here.

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_panel(request):

    return render(request, 'admin_panel.html')


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admindashboard(request):
    if request.user.is_authenticated:
        today_sales = Payment.objects.filter(created_at=datetime.today(), paid=True).aggregate(Sum('amount_paid'))['amount_paid__sum']
        # Total sales and revenue
        orders_count = Order.objects.filter(status__in=['Order Confirmed', 'Shipped', 'Out for delivery']).count()
        total_sales = Payment.objects.filter(paid=True).count()
        total_revenue = OrderProduct.objects.filter(order__status='Delivered').annotate(total_price=F('product_price') * F('quantity')).aggregate(Sum('total_price'))['total_price__sum']
        # Render the template with the data
        if today_sales is not None:
            today_sales = round(today_sales,2)
        if total_sales is not None:
            total_sales = round(total_sales)
        if total_revenue is not None:
            total_revenue = round(total_revenue,2)
        
        context = {
                'orders_count': orders_count,
                'today_sales': today_sales,
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                
            }
        
        return render(request, 'dashbord.html',context)
    else: 
        return redirect('admin_login')
 
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login') 
def manage_order(request):
    orders=Order.objects.all().order_by('-id')
    paginator = Paginator(orders, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    
    return render(request, 'manageorder.html', locals())

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def manage_order_conf(request):
    
    return render(request,'manage_order_conf.html')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def orderdetails(request, id):
    orders=Order.objects.get(pk=id)
    products = OrderProduct.objects.filter(order=orders)
    addrs =orders.address
    context = {
        'product': products,
        'addrs': addrs,
        'order': orders
    }
    return render(request, 'orderdetails.html',context)

@user_passes_test(lambda u:u.is_superuser,login_url='adminlogin')
def searchorder(request):
    keyword = request.GET.get('name')
    print(keyword)
    orders = Order.objects.filter(Q(address__firstname__icontains=keyword) | Q(address__email__icontains=keyword) | Q(status__icontains=keyword) | Q(payment__payment_method__icontains=keyword) | Q(order_number__icontains=keyword)).order_by('-id')
    paginator = Paginator(orders, 8)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr) 
    return render(request, 'manageorder.html', locals())

@user_passes_test(lambda u:u.is_superuser,login_url='adminlogin')
def update_order(request, id):
    if request.method == 'POST':
        order = Order.objects.get(id=id)
        status = request.POST.get('status')
        if(status):
            order.status = status
            order.save()
        if status  == "Delivered":
            try:
                payment = Payment.objects.get(payment_id = order.order_number, status = False)
                print(payment)
                if payment.payment_method == 'Cash on Delivery':
                    payment.paid = True
                    payment.save()
            except:
                pass
    return redirect('manage_order')

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admincancelOrder(request, id):

    client = razorpay.Client(auth=("rzp_test_aCOPLFUFmC265M", "xOMWffWBSmuJi5y06YT3aq4N"))
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(manage_order)
    
    payment=order.payment
    msg=''
    
    if (payment.payment_method == 'Paid by Razorpay'):
        payment_id = payment.payment_id
        amount = payment.amount_paid
        amount= amount*100
        try :
            captured_amount = client.payment.capture(payment_id,amount)
        except BadRequestError as e:
            # Handle a BadRequestError from Razorpay
            captured_amount = None
            messages.warning(request,'The payment has not been captured,We cant Refund the money')
            return redirect(manage_order)
        #   except ServerError as e:
              # Handle a ServerError from Razorpay
        #   captured_amount = None
            # msg = "Server error occurred while capturing the payment."

        if captured_amount is not None and captured_amount['status'] == 'captured' :
            refund_data = {
                "payment_id": payment_id,
                "amount": amount,  # amount to be refunded in paise
                "currency": "INR",
            }
            
            refund = client.payment.refund(payment_id, refund_data)
            #  except BadRequestError as e:
            #      # Handle a BadRequestError from Razorpay
            #      refund = None
            #      msg = "Bad request error occurred while processing the refund."
            #  except ServerError as e:
            #      # Handle a ServerError from Razorpay
            #      refund = None
            #      msg = "Server error occurred while processing the refund."
            print(refund)
            
            if refund is not None:
                current_user=request.user
                order.refund_completed = True
                order.status = 'Cancelled'
                payment = order.payment
                payment.refund_id = refund['id']
                payment.save()
                order.save()
                messages.success(request,'The order has been successfully cancelled and amount has been refunded!')
                mess=f'Hai\t{current_user.username},\nYour order has been canceled, Money will be refunded with in 1 hour\nThanks!'
                try:
                    send_mail(
                            "Order Cancelled",
                            mess,
                            settings.EMAIL_HOST_USER,
                            [current_user.email],
                            fail_silently = False
                        )
                except Exception as e:
                    # Handle an exception while sending email
                    msg += "\nError occurred while sending an email notification."
            else :
                messages.warning(request,'The order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'THE ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'The payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'THE ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect(manage_order)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def addcategory(request):
    if request.method == "POST":
        name = request.POST['name']
        if Category.objects.filter(name__iexact=name.lower().replace(' ', '')).exists():
            messages.warning(request,'category already exist')

        else:
            Category.objects.create(name=name)
            messages.success(request,'category created successfully')
            return redirect(viewcategory)
    return render(request, 'addcategory.html', locals())



@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def viewcategory(request):

    category = Category.objects.all().order_by('-id')
    context={
        'category':category
    }
    
    return render(request, 'viewcategory.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def editcategory(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        name = request.POST['name']

        if Category.objects.exclude(id=category_id).filter(name__iexact=name.lower().replace(' ', '')).exists():
            messages.warning(request,'Category already exists')

        else:
            category.name = name
            category.save()
            messages.success(request,'Category updated successfully')
            return redirect(viewcategory)

    context = {
        'category': category
    }

    return render(request, 'categoryedit.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def deletecategory(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully')
    return redirect(viewcategory)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def disable_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.is_disable = True
    category.save()
    return redirect(viewcategory)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def enable_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.is_disable = False
    category.save()
    return redirect(viewcategory)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def searchcategory(request):
    keyword = request.GET.get('name')
    print(keyword)
    category = Category.objects.filter(Q(name__icontains=keyword)).order_by('id')
    paginator = Paginator(category, 6)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr) 
    return render(request, 'viewcategory.html',locals())






# @user_passes_test(lambda u:u.is_superuser,login_url='admindb')
# def addcategory(request):
#     category = request.GET.get('newcategory')
#     if Category.objects.filter(name=category).exists():
#         messages.info(request,'Name entered has an existing Category')
#         return redirect(request, 'addcategory.html')
#     else :
#         Category.objects.create(name=category)
#         messages.success(request,"New Category Is Added")
#     return redirect(viewcategory)                  


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def addproduct(request):
    category = Category.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        categ = request.POST['categories']
        desc = request.POST['desc']
        catobj = Category.objects.get(id=categ)
        if Product.objects.filter(category=catobj, name=name).exists():
            messages.warning(request,'Product already exist')
            return redirect(viewproduct)
        product = Product.objects.create(name=name, category=catobj, description=desc)
        product.save()
        messages.success(request, "Product Added")
        return redirect(viewproduct)
    return render(request, 'addproduct.html',locals())

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def viewproduct(request):
    product = Product.objects.all().order_by('id')
    variant = Variant.objects.all().order_by('id')
    paginator = Paginator(product, 10)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr)
    dict_prod = {
        'variant': variant,
        'product' : product,
        'page_obj': page_obj
    }
    return render(request, 'viewproduct.html',dict_prod)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def searchproduct(request):
    keyword = request.GET.get('name')
    print(keyword)
    product = Product.objects.filter(Q(name__icontains=keyword) | Q(category__name__icontains=keyword)).order_by('id')
    variant = Variant.objects.all().order_by('id')
    paginator = Paginator(product, 6)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr) 
    dict_prod = {
        'variant': variant,
        'product' : product,
        'page_obj': page_obj
    }
    return render(request, 'viewproduct.html',dict_prod)


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def editproduct(request, id):
    editted = Product.objects.get(pk= id)
    category = Category.objects.all()
    if request.method == 'POST':
        editted.name= request.POST['name']
        ctgry = request.POST['categories']
        editted.description = request.POST['desc']
        catobj = Category.objects.get(id=ctgry)
        editted.category = catobj
        editted.save()
        messages.success(request, "Product Editted Successfully")
        return redirect('viewproduct')
    
    context = {
        'category' : category,
        'editted' : editted
    }
    return render(request, 'editproduct.html',context)


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def productdetails(request, id):
    variant = Variant.objects.all().order_by('id')
    editted = Product.objects.get(pk= id)
    category = Category.objects.all()
    
    context = {
        'var' : variant,
        'category' : category,
        'editted' : editted
    }
    return render(request, 'productdetails.html',context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def deleteproduct(request,id):
    category=get_object_or_404(Product,id=id)
    category.delete()
    messages.warning(request, "Product Deleted")
    return redirect(viewproduct)



@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def viewvariant(request):
    product = Variant.objects.all().order_by('id')
    
    paginator = Paginator(product, 6)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr)
    dict_prod = {
        'product' : product,
        'page_obj': page_obj
    }
    return render(request, 'viewvariant.html',dict_prod)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def searchvariant(request):
    keyword = request.GET.get('name')
    print(keyword)
    product = Variant.objects.filter(Q(product__name__icontains=keyword) | Q(color__icontains=keyword) | Q(category__name__icontains=keyword)).order_by('id')
    paginator = Paginator(product, 6)
    page_numebr = request.GET.get('page')
    page_obj = paginator.get_page(page_numebr) 
    dict_prod = {
        'product' : product,
        'page_obj': page_obj
    }
    return render(request, 'viewvariant.html',dict_prod)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def addvariant(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        color = request.POST['color']
        price = request.POST['price']
        img1 = request.FILES['img1']
        img2 = request.FILES['img2']
        img3 = request.FILES['img3']
        if Variant.objects.filter(product=product, color=color).exists():
            messages.warning(request,'Variant already exist')
            return redirect('productdetails', id)
        categ = product.category.id
        catobj = Category.objects.get(id=categ)
        variant = Variant.objects.create(product=product, color=color, price=price, category=catobj, img1=img1, img2=img2, img3=img3)
        variant.save()
        messages.success(request, "Variant Added")
        return redirect('productdetails', id)
    context = {
        'product' : product,
    }
    return render(request, 'addvarient.html',context)


@user_passes_test(lambda u:u.is_superuser,login_url='adminlogin')
def addsizeandstock(request, id):
    var = Variant.objects.get(pk=id)
    selection=['XS','S','M','L','XL','XXL','XXXL','7','8','9','10','11','12','28','30','32','34','36','38','40','42']
    if request.method == 'POST':
        stock = request.POST['stock']
        size = request.POST['size']
        if Size.objects.filter(variant=var, size=size).exists():
            messages.warning(request,'Size already exist you can add stock')
            return redirect('editvariant', var.id)
        variantsize = Size.objects.create(variant=var, size=size, stock=stock)
        variantsize.save()
        messages.success(request, "Size and Stock Added")
        return redirect('editvariant', var.id)
    
    return render(request, 'addsizeandstock.html',locals())


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def editvariant(request, id):
    editted = Variant.objects.get(pk= id)
    product = Product.objects.all()
    sizes = Size.objects.filter(variant=editted)

    if request.method == 'POST':
        prod = request.POST['Product']
        prd = Product.objects.get(id=prod)
        categ = prd.category.id
        catobj = Category.objects.get(id=categ)
        editted.category = catobj
        editted.product = prd
        editted.color = request.POST['color']
        editted.price = request.POST['price']
        if 'img1' in request.FILES:
            editted.img1 = request.FILES['img1']
        if 'img2' in request.FILES:           
            editted.img2 = request.FILES['img2']
        if 'img3' in request.FILES:
            editted.img3 = request.FILES['img3']
        editted.save()
        for size in sizes:
            size_id = str(size.id)
            size.size = request.POST['size'+size_id]
            size.stock = request.POST['stock'+size_id]
            # size.size = request.POST['size']
            # size.stock = request.POST['stock']
            size.save()
        messages.success(request, "Editted Successfully")
        return redirect('viewproduct')
    
    context = {
        'size' : sizes,
        'product' : product,
        'editted' : editted,
       
    }
    return render(request, 'editvariant.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def deletevariant(request,id):
    category=get_object_or_404(Variant,id=id)
    category.delete()
    messages.warning(request, "Variant Deleted")
    return redirect(viewproduct)


# def editvariant(request, id):
#     variant = Variant.objects.get(pk=id)
#     product = variant.product
#     sizes = Size.objects.filter(variant=variant)
#     if request.method == 'POST':
#         for size in sizes:
#             size_id = str(size.id)
#             size.size = request.POST.get('size_'+size_id)
#             size.stock = request.POST.get('stock_'+size_id)
#             size.save()
#         return redirect('viewproduct')
#     return render(request, 'editvariant.html', {'product': product, 'sizes': sizes})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def deletesize(request,id):
    size=get_object_or_404(Size,id=id)
    size.delete()
    vid = size.variant.id
    messages.warning(request, "Variant Size Deleted")
    return redirect('editvariant', vid)


def view_coupon(request):
    coupon=Coupon.objects.all()
    return render(request,"adminpanel/viewcoupon.html",locals())

def add_coupons(request):
    coupon_form = CouponForm(instance=request.user)
    if request.method == 'POST':
        coupon_form= CouponForm(request.POST)
        if coupon_form.is_valid():
            coupon_form.save()
            return redirect('view_coupon')
    else:
        form = CouponForm()
    return render(request, 'adminpanel/addcoupon.html', {'coupon_form': coupon_form})

def edit_coupon(request, pid):
    coupon = Coupon.objects.get(id=pid)
    coupon_form = CouponForm(instance=request.user)
    if request.method == "POST":
        coupon_form = CouponForm(request.POST,instance=coupon)
        if coupon_form.is_valid():
            coupon_form.save()
            messages.success(request, "Coupon Updated")
            return redirect('view_coupon')
    else:
        coupon_form = CouponForm(instance=coupon)
        messages.error(request, "fill all fields")

    return render(request, 'adminpanel/editcoupon.html', {'coupon_form': coupon_form, 'coupon': coupon})

def delete_coupon(request, pid):
    try:
        Coupon.objects.get(id=pid).delete()
        messages.success(request, "Coupon Deleted")
    except:
        messages.warning(request,'some thing wrong happend')
        
    return redirect('view_coupon')




@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def sales(request):
    return render(request, 'sales.html')


@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def list_users(request):
    user_list = Customer.objects.all().order_by('id')
    paginator = Paginator(user_list, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'users.html', {'page_obj': page_obj})

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def blockuser(request, id):
    # user = get_object_or_404(User, id=id)
    user=Customer.objects.get(id=id)
    if user.is_active:
        user.is_active = False
        messages.success(request, "user has been blocked.")
    else:
        user.is_active = True
        messages.success(request, "user has been unblocked.")
    user.save()
    return redirect(list_users)





def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('dashbord')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            request.session['is_admin_logged_in'] = True
            return redirect('dashbord')
        else:
            messages.error(request, 'Invalid credentials or not authorized.')
            return redirect('admin_login')
    else:
        return render(request, 'admin_login.html')




def admin_logout(request):
    auth.logout(request)
    # request.session['is_admin_logged_in'] = False
    return redirect('home')

