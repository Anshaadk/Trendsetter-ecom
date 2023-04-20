from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import auth,messages
from django.contrib.auth.models import User
from admin_side.views import *
from user_side.views import *
from .forms import *
from .models import *
from django.core.mail import send_mail,EmailMessage
import random
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from user_side.views import _cart_id
from django.contrib.auth.forms import PasswordChangeForm
import requests






# Create your views here.
def login(request):
    if request.method=='POST':
        user_name=request.POST['username']
        pass_word=request.POST['password']
        user =auth.authenticate(username=user_name,password=pass_word) 
        print(user)
        if user is not None: 
            try:
                cart = Cart.objects.get(car_id=_cart_id(request))
                is_cart_item_exists=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item =CartItem.objects.filter(cart=cart)
                    
                    product_variations = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variations.append(list(variation))
                    
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pr in product_variations:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id=id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user =user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            
                            for item in cart_item:
                                item.user =user
                                item.save()
            except:
                pass
            auth.login(request,user)
            url = request.META.get('HTTP_REFERER') 
            try:
                query = requests.utils.urlparse(url).query 
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
                
            except:
                return redirect(home)
        else:
            messages.warning(request,f'Password or Username is Wrong ')            
            return redirect(login)
    return render(request,'login.html')

def register(request):
    usr = None
    #Register Form
    if request.method=='POST':
        get_otp=request.POST.get('otp')
        # OTP Verification
        if get_otp:
            get_usr=request.POST.get('usr')
            usr=Customer.objects.get(username=get_usr)
            if int(get_otp)==UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active=True
                usr.save()
                messages.success(request,f'Account is created for {usr.username}')
                return redirect(login)
            else:
                messages.warning(request,f'You Entered a wrong OTP')
                return render(request,'register.html',{'otp':True,'usr':usr})
        form = CreateUserForm(request.POST)
        #Form Validation
        if form.is_valid():
            form.save()
            email=form.cleaned_data.get('email')
            username=form.cleaned_data.get('username')
            usr=Customer.objects.get(username=username)
            usr.email=email
            usr.username=username
            usr.is_active=False
            usr.save()
            usr_otp=random.randint(100000,999999)
            UserOTP.objects.create(user=usr,otp=usr_otp)
            mess=f'Hello\t{usr.username},\nYour OTP to verify your account for Trendsetter is {usr_otp}\nThanks!'
            send_mail(
                    "welcome to Trendsetter -Verify your Email",
                    mess,
                    settings.EMAIL_HOST_USER,
                    [usr.email],
                    fail_silently=False
                )
            messages.info(request,f'OTP send to your email')

            return render(request,'register.html',{'otp':True,'usr':usr})
            
        else:
            errors = form.errors
            for field, errors in errors.items():
              for error in errors:
                messages.error(request, f" {error}")
                       
    #Resend OTP
    elif (request.method == "GET" and 'username' in request.GET):
        get_usr = request.GET['username']
        if (Customer.objects.filter(username = get_usr).exists() and not Customer.objects.get(username = get_usr).is_active):
            usr = Customer.objects.get(username=get_usr)
            id = usr.id
            
            otp_usr = UserOTP.objects.get(user_id=id)
            usr_otp=otp_usr.otp
            mess = f"Hello, {usr.username},\nYour OTP is {usr_otp}\nThanks!"
            
            send_mail(
        "Welcome to Trendsetter - Verify Your Email",
        mess,
        settings.EMAIL_HOST_USER,
        [usr.email],
        messages.success(request, f'OTP resend to  {usr.email}'),

        # fail_silently = False
         )
        return render(request,'register.html',{'otp':True,'usr':usr})
    else:
            errors = ''
    form=CreateUserForm()
    context = {'form': form, 'errors': errors}

    return render (request, 'register.html', context)

def logout(request):
    auth.logout(request)
    # if 'username' in request.session:
    #     request.session.flush()
    return redirect(home)


def forgetpassword(request):
    if request.method=="POST":
        email=request.POST['email']
        if Customer.objects.filter(email=email).exists():
            user=Customer.objects.get(email__exact=email)
           #reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site,
             
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                 # Generate a token for a user also
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email=EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            send_email.send()

            messages.success(request,"Password reset email has been sent to your email")
            
            return redirect('login')
        else:
            messages.error(request,'Account does not exists')
            return redirect('login')
    return render(request,'forgetpassword.html')



def resetpassword_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Customer._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError,Customer.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request,"  Please reset your password")
        return redirect('resetpassword')
    else:
        messages.error(request,"This link has been expired")
        return redirect('login')

    

    
# @login_required(login_url='login')
# @never_cache   
def resetpassword(request):
   if request.method=="POST":
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password == confirm_password:
            uid=request.session.get('uid')
            user= Customer.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful")
            return redirect('login')
        else:
          messages.error(request,"Password not match")
          return redirect('resetPassword')
   else:
     return render (request,'resetPassword.html')
 
def updateprofile(request):
    user_id= request.user.id
    user = Customer.objects.get(pk=user_id)

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=user)
        
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('myaccount')
        else:
            messages.error(request, 'There was an error while updating your profile.')
    else:
        form = UpdateUserForm(instance=user)
        context = {'form': form}
    return render(request, 'updateprofile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password was successfully updated!')
            update_session_auth_hash(request, user)
            return redirect(myaccount)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'changepassword.html', {'form': form})


def login_required_decorator(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper

change_password = login_required_decorator(change_password)

def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('manageaddress')
    else:
        form = AddressForm()
    return render(request, 'add_address.html', {'form': form})

def confi_add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('checkout')
    else:
        form = AddressForm()
    return render(request, 'add_address.html', {'form': form})


def edit_address(request,id):
    address = get_object_or_404(AddressDetails, id=id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('manageaddress')
    else:
        form = AddressForm(instance=address)

    return render(request, 'edit_address.html', {'form': form})


def manageaddress(request):
    user=request.user
    add=AddressDetails.objects.filter(user_id=user.id)
    
    return render(request,'manageaddress.html',locals())

def deleteaddress(request,id):
    dele=AddressDetails.objects.get(id=id)
    dele.delete()
    return redirect(manageaddress)

def disable_address(request, id):
    address = AddressDetails.objects.get(id=id)
    address.is_disable = True
    address.save()
    return redirect(manageaddress)

def enable_address(request, id):
    address = AddressDetails.objects.get(id=id)
    address.is_disable = False
    address.save()
    return redirect(manageaddress)


def error_404(request, exception):
   context = {}
   return render(request,'404.html', context)
