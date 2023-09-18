import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from user_side.models import *
from admin_side.models import *
from account.models import *
from user_side.views import _cart_id
from user_side.views import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from razorpay.errors import BadRequestError,ServerError
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
import os
from user_side import *
import trendsetter.settings

def confirmation(request, id):
    # try:
        cart_items=CartItem.objects.filter(user=request.user)
        # newAddress_id = request.POST.get('selected_addresses')
        addressid = request.POST.get('address')
        if addressid == None:
            messages.warning(request, "Please Select Your Address,  Or Add A New Address.")
            return redirect(checkout)
        address = AddressDetails.objects.get(pk=addressid)
        total=request.POST.get('total')
        Shipping=request.POST.get('shipping')
        amountToBePaid=request.POST.get('amountToBePaid')
        user = Customer.objects.get(pk=id)
        
        
        # if not newAddress_id:
        #     messages.error(request,'Select An Address to Proceed to Checkout.')
        #     return redirect(checkout)
        # else:
        #     address  = Address.objects.get(id = newAddress_id)

    # except ObjectDoesNotExist:
        # pass
        context={
            'cart_items':cart_items,
            'addressSelected':address,
            'shippingcharge':Shipping,
            'amountToBePaid':amountToBePaid,
            'total':total,
            'user':user,
                }
        return render(request, 'main/confirmation.html', context)

def calculateCartTotal(request):
   cart_items   = CartItem.objects.filter(user=request.user)
   if not cart_items:
       pass
    #   return redirect('product_management:productlist',0)
   else:
      total = 0
      tax=0
      grand_total=0
      for cart_item in cart_items:
         total  += (cart_item.product.price * cart_item.quantity)
         tax = 50
         grand_total = tax + total
   return total, tax, grand_total


# @login_required(login_url='login')
# @csrf_protect

  
def placeOrder(request):
   if request.method =='POST':
         
         newAddress_id = request.POST.get('addressSelected')
         address = AddressDetails.objects.get(id = newAddress_id)
         newOrder =Order()
         newOrder.user=request.user
         newOrder.address = address
         yr = int(datetime.date.today().strftime('%Y'))
         dt = int(datetime.date.today().strftime('%d'))
         mt = int(datetime.date.today().strftime('%m'))
         d = datetime.date(yr,mt,dt)
         current_date = d.strftime("%Y%m%d")
         rand = str(random.randint(1111111,9999999))
         order_number = current_date + rand
         newPayment = Payment()
         if('payment_id' in request.POST ):
            newPayment.payment_id = request.POST.get('payment_id')
            newPayment.paid = True
         else:
            newPayment.payment_id = order_number
            payment_id  =order_number
         newPayment.payment_method = request.POST.get('payment_method')
         newPayment.customer = request.user
         newPayment.save()
         newOrder.payment = newPayment
         try :
            total, tax, grand_total = calculateCartTotal(request)
         except:
             messages.success(request,  "Your Order Is Already Placed.")
             return redirect('viewcart')
         newOrder.order_total = grand_total
        
         newOrder.paid_amount = grand_total
         newPayment.amount_paid = grand_total
         newPayment.save()
         newOrder.payment = newPayment
         order_number = 'Trendsetter'+ order_number
         newOrder.order_number =order_number
        #  #to making order number unique
         while Order.objects.filter(order_number=order_number) is None:
            order_number = 'Trendsetter'+order_number
         newOrder.tax=tax
         newOrder.save()
         newPayment.order_id = newOrder.id
         newPayment.save()
         newOrderItems = CartItem.objects.filter(user=request.user)
         for item in newOrderItems:
            OrderProduct.objects.create(
                order = newOrder,
                customer=request.user,
                product=item.product,
                product_price=item.product.price,
                quantity=item.quantity
            )
            #TO DECRESE THE QUANTITY OF PRODUCT FROM CART
            variant = Variant.objects.filter(id=item.product_id).first()
            s= item.size
            orderproduct = Size.objects.filter(variant=variant, size=s).first()
            if(orderproduct.stock<=0):
               messages.warning(request,'Sorry, Product out of stock!')
               orderproduct.is_available = False
               orderproduct.save()
               item.delete()
               return redirect('viewcart')
            elif(orderproduct.stock < item.quantity):
               messages.success(request,  f"{orderproduct.stock} only left in cart.")
               return redirect('viewcart')
            else:
               orderproduct.stock -=  item.quantity
            orderproduct.save()
        #  if(instance):
        #     instance.order = newOrder
        #     instance.save()
        # TO CLEAR THE USER'S CART
         cart_item=CartItem.objects.filter(user=request.user)
         cart_item.delete()
         messages.success(request,'Order Placed Successfully')
         payMode =  request.POST.get('payment_method')
         if (payMode == "Paid by Razorpay" ):
            return JsonResponse ({'order_number':order_number,'status':"Your order has been placed successfully"})
         elif (payMode == "COD" ):
            request.session['my_context'] = {'payment_id':payment_id}
            return redirect('order_complete', newOrder.order_number )
   return redirect('checkout')


@login_required(login_url='login')
@csrf_protect
def orderComplete(request,ordernumber):
    order = Order.objects.get(order_number=ordernumber)
    orderitems = OrderProduct.objects.filter(order=order)
    context={
        'total':order.order_total,
        'order': order,
        'orderitems':orderitems,    
        # 'product_items': product_items,
    }

    return render(request, 'main/order_completed.html',context)

def checkCoupon(request):
   try:
      coupon_code = request.POST.get('couponCode')
      coupon = Coupon.objects.get(code = coupon_code)
      try:
         instance = UserCoupon.objects.get(user=request.user, coupon=coupon)
      except ObjectDoesNotExist:
         instance = None
         if(instance):
            pass
         else:
            instance = UserCoupon.objects.create(user = request.user ,coupon = coupon)
   except:
      instance = None
   return instance

def orderComplete(request,ordernumber) :

    order = Order.objects.get(user=request.user,order_number=ordernumber)
    orderitem = OrderProduct.objects.filter(customer=request.user,order=order)

    return render(request,'main/order_completed.html',locals())
 
#  @login_required(login_url='login')

def cancelOrder(request):
    if request.method == 'POST':
            id = request.POST.get('id')

    client = razorpay.Client(auth=(trendsetter.settings.API_KEY, trendsetter.settings.RAZORPAY_SECRET_KEY))
    try:
        order = Order.objects.get(id=id,user=request.user)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        order = None
    
    if order is None:
        # Render an error message if the order does not exist
        messages.warning(request,'The order you are trying to cancel does not exist.')
        return redirect(viewOrder)
    
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
            messages.warning(request,'The payment has not been captured.Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
            return redirect(viewOrder)
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
                messages.success(request,'Your order has been successfully cancelled and amount has been refunded!')
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
                messages.warning(request,'Your order is not cancelled because the refund could not be completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!')
                pass
        else :
            if(payment.paid):
                order.refund_completed = True
                order.status = 'Cancelled'
                messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
                order.save()
            else:
                order.status = 'Cancelled'
                order.save()
                messages.success(request,'Your payment has not been recieved yet. But the order has been cancelled.!')
    else :
        order.status = 'Cancelled'
        messages.success(request,'YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!')
        order.save()
    return redirect('orderbook')

