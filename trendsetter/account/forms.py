from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm




#regitration

class CreateUserForm(UserCreationForm):
   password1=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Enter Password',                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}))
   password2=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password',                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}))
   class Meta:
        model = Customer
        fields = ['username', 'email','password1', 'password2']
        widgets = { 
            'username': forms.TextInput(attrs=
                                        {'placeholder': 'Username',
                                         'class':'form-control',
                                         'style':'max-width:300px; margin-left:115px'
                                         
                                         }),
            'email': forms.TextInput(attrs={'placeholder': 'Email',
                                            'class':'form-control',
                                         'style':'max-width:300px;  margin-left:115px'}),
            
             }

class UpdateUserForm(UserChangeForm):
    

    class Meta:
        model = Customer
        fields = [ 'phone', 'first_name', 'profile_pic','last_name', 'address','city', 'state', 'pincode']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter Your First Name','class':'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Your Last Name','class':'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Your Phone Number','class':'form-control'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Your Address','class':'form-control'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter Your State','class':'form-control'}),
            'pincode': forms.NumberInput(attrs={'placeholder': 'Enter Your Pincode','class':'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter Your City','class':'form-control'}),




         }


        
form = UpdateUserForm(initial={'city': Customer.username})

class AddressForm(forms.ModelForm):
    class Meta:
        model = AddressDetails
        fields = ('first_name', 'last_name', 'phone', 'email', 'order_address', 'city', 'state', 'country', 'zip_code')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter Your First Name','class':'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter Your Last Name','class':'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter Your Phone Number','class':'form-control'}),
            'country': forms.TextInput(attrs={'placeholder': 'Enter Your Address','class':'form-control'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter Your State','class':'form-control'}),
            'zip_code': forms.NumberInput(attrs={'placeholder': 'Enter Your Pincode','class':'form-control'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter Your City','class':'form-control'}),
            'email': forms.TextInput(attrs={'placeholder': 'Enter Your Email','class':'form-control'}),
            'order_address': forms.TextInput(attrs={'placeholder': 'Landmark','class':'form-control'}),
            
            
        }